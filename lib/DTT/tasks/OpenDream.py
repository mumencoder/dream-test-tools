
from .common import *

from .Install import *
from .Tests import *
from .Git import *
from .Compare import *
from .TestCase import *

class OpenDream(object):
    def source_from_github(env):
        async def task(penv, senv):
            base.OpenDream.Source.from_github(senv)
        return Shared.Task(env, task, ptags={'action':'source_from_github'})

    def create_shared_repos(env):
        async def task(penv, senv):
            senv.attr.resources.shared_opendream_repo = OpenDreamRepoResource(env, senv.attr.source.id, limit=4)
            for i in range(0, 4):
                denv = penv.branch()
                base.OpenDream.Source.load(denv, f'{senv.attr.source.id}.copy.{i}')
                await Shared.Path.full_sync_folders(senv, senv.attr.source.dir, denv.attr.source.dir)
            penv.attr.self_task.export( senv, ".resources.shared_opendream_repo" )
        t1 = Shared.Task(env, task, ptags={'action':'create_shared_repos'})
        return t1

    def acquire_shared_repo(env):
        async def task(penv, senv):
            while True:
                repo = await senv.attr.resources.shared_opendream_repo.acquire()
                if repo is not None:
                    break
                await asyncio.sleep(0.1)
            penv.attr.self_task.guard_resource( senv.attr.resources.shared_opendream_repo, repo )
            senv.attr.git.repo.local_dir = repo["data"]["path"]
            senv.attr.git.repo.remote = 'origin'
            await Shared.Git.Repo.ensure(senv)

            base.OpenDream.Source.load( senv, repo["data"]["source_id"] )
            senv.attr.opendream.shared_repo = repo
        return Shared.Task(env, task, ptags={'action':'acquire_shared_repo'}, unique=False)

    def release_shared_repo(env):
        async def task(penv, senv):
            senv.attr.resources.shared_opendream_repo.release(senv.attr.opendream.shared_repo)
            penv.attr.self_task.unguard_resource( senv.attr.opendream.shared_repo )
        return Shared.Task(env, task, ptags={'action':'release_shared_repo'}, unique=False)

    def load_install_from_local(env, local_name, local_dir):
        async def task(penv, senv):
            senv.attr.source.dir = local_dir
            senv.attr.git.repo.local_dir = local_dir
            Shared.Git.Repo.load(senv)
            base.OpenDream.Install.load(senv, f'local.{local_name}')
            senv.attr.platform_cls = base.OpenDream
            Install.config(senv)
        return Shared.Task(env, task, ptags={'action':'load_install_from_local'}, stags={'local_name':local_name} )

    def load_install_from_github(env):
        def process_tags(penv, senv):
            senv.attr.platform_cls = base.OpenDream
            base.OpenDream.Install.from_github(senv)
            Install.config(senv)
            return {'install':senv.attr.install.id} 
        async def task(penv, senv):
            pass
        return Shared.Task(env, task, ptags={'action':'load_install_from_github'}, process_tags=process_tags )

    def wait_for_commit(env, commit_id):
        async def task(penv, senv):
            while commit_id not in senv.attr.opendream.commits:
                await asyncio.sleep(0.5)
        return Shared.Task(env, task, ptags={'action':'wait_for_commit', 'commit_id':commit_id}, unique=False )
        
    def process_pr_commits(env, process_task):
        async def task(penv, senv):
            if await senv.attr.opendream.processed_commits.check_add( senv.attr.pr.base_commit ) is False:
                base_tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.pr.base_commit), 
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task() )
                Shared.Task.link( penv.attr.self_task, base_tasks ) 
                Shared.Task.link( base_tasks, bottom, ltype="exec" )
            else:
                task = OpenDream.wait_for_commit( env, senv.attr.pr.base_commit)
                Shared.Task.link( penv.attr.self_task, task )
                Shared.Task.link( task, bottom, ltype="exec")
            if await senv.attr.opendream.processed_commits.check_add( senv.attr.pr.merge_commit ) is False:
                # TODO: better way to do this
                if senv.attr.pr.info['id'] == 748018792:
                    extra_task = Shared.Task.set_senv(env, '.compilation.args', {'flags':['experimental-preproc']})
                else:
                    extra_task = Shared.Task.nop(env)

                merge_tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.pr.merge_commit), 
                    extra_task,
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task() )
                Shared.Task.link( penv.attr.self_task, merge_tasks )
                Shared.Task.link( merge_tasks, bottom, ltype="exec" )
            else:
                task = OpenDream.wait_for_commit( env, senv.attr.pr.merge_commit)
                Shared.Task.link( penv.attr.self_task, task )
                Shared.Task.link( task, bottom, ltype="exec")

        top = Shared.Task(env, task, ptags={'action':'process_pr_commits'} )
        bottom = Shared.Task.group(env, 'process_pr_commits_end')
        Shared.Task.link( top, bottom )
        return Shared.TaskBound(top, bottom)

    def process_history_commit(env, process_task):
        async def task(penv, senv):
            if await senv.attr.opendream.processed_commits.check_add( senv.attr.git.repo.commit ) is False:
                tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.git.repo.commit), 
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task() )
                Shared.Task.link( penv.attr.self_task, tasks )
                Shared.Task.link( tasks, bottom, ltype="exec" )
            else:
                task = OpenDream.wait_for_commit( env, senv.attr.git.repo.commit)
                Shared.Task.link( penv.attr.self_task, task )
                Shared.Task.link( task, bottom, ltype="exec")

        top = Shared.Task(env, task, ptags={'action':'process_history_commits'} )
        bottom = Shared.Task.group(env, 'process_history_commits_end')
        Shared.Task.link( top, bottom )
        return Shared.TaskBound(top, bottom)

    def process_commit(env):
        def no_incomplete_tests(penv, senv):
            return len(senv.attr.tests.incomplete) == 0

        async def task(penv, senv):
            senv.attr.opendream.commits[ senv.attr.git.repo.commit ] = senv
            if no_incomplete_tests(penv, senv):
                penv.attr.self_task.halt()
                return

            await Shared.Path.sync_folders( penv, senv.attr.source.dir, senv.attr.install.dir )
            senv.attr.dotnet.solution.path = senv.attr.install.dir
            senv.attr.resources.opendream_server = Shared.CountedResource(1)
            await base.OpenDream.Builder.build(senv)

            if not base.OpenDream.Builder.build_ready(senv):
                penv.attr.self_task.halt()

        return Shared.Task(env, task, ptags={'action':'process_commit'})

    def initialize_github_compares(env):
        async def task(penv, senv):
            senv.attr.pr.compares = []
            senv.attr.history.compares = []
            senv.attr.repo_report = reports.GithubRepoReport(senv)
            penv.attr.self_task.export( senv, ".pr.compares" )
            penv.attr.self_task.export( senv, ".history.compares" )
            penv.attr.self_task.export( senv, ".repo_report" )

        return Shared.Task(env, task, ptags={'action':'initialize_github_compares'})

    def load_pr_compare(env):
        async def task(penv, senv):
            benv = env.branch()
            base.Byond.Install.load(benv, env.attr.compares.ref_version)
            compare = {'pull_info': senv.attr.pr.info,
                'ref_env':benv, 
                'base_env':senv.attr.opendream.commits[senv.attr.pr.base_commit], 
                'merge_env':senv.attr.opendream.commits[senv.attr.pr.merge_commit]
            }
            senv.attr.pr.compares.append(compare)
        return Shared.Task(env, task, ptags={'action':'load_pr_compare'})

    def load_history_compares(env):
        async def task(penv, senv):
            i = 0
            while i+1 < len(senv.attr.history.infos):
                merge_info = senv.attr.history.infos[i]
                base_info = senv.attr.history.infos[i+1]

                benv = env.branch()
                base.Byond.Install.load(benv, env.attr.compares.ref_version)
                compare = {'history_info': merge_info,
                    'ref_env':benv, 
                    'base_env':senv.attr.opendream.commits[base_info["sha"]], 
                    'merge_env':senv.attr.opendream.commits[merge_info["sha"]]
                }
                senv.attr.history.compares.append(compare)
                i += 1
        return Shared.Task(env, task, ptags={'action':'load_history_compares'})

    def pr_compare_report(env):
        async def task(penv, senv):
            compares = senv.attr.pr.compares
            cenvs = {}
            for tenv in TestCase.list_all(penv.branch(), penv.attr.tests.dirs.dm_files):
                TestCase.load_test_text(tenv)
                TestCase.wrap(tenv)
                for compare in compares:
                    cid = compare['pull_info']['id']
                    if cid not in cenvs:
                        cenv = penv.branch()
                        cenvs[cid] = cenv
                        cenv.attr.pr.info = compare['pull_info']
                        cenv.attr.compare.ref = compare['ref_env'].branch()
                        cenv.attr.compare.prev = compare['base_env'].branch()
                        cenv.attr.compare.next = compare['merge_env'].branch()
                        cenv.attr.compare.report = reports.CompareReport(cenv)
                        senv.attr.repo_report.add_pr( cenv )

                    ctenv = cenvs[cid].branch()
                    ctenv.attr.compare.ref = compare['ref_env'].branch()
                    ctenv.attr.compare.prev = compare['base_env'].branch()
                    ctenv.attr.compare.next = compare['merge_env'].branch()
                    Compare.compare_test(ctenv, tenv)
                    senv.attr.repo_report.get_pr(cid).attr.compare.report.add_compare_test( ctenv )
        return Shared.Task(env, task, ptags={'action':'pr_compare_report'})

    def history_compare_report(env):
        async def task(penv, senv):
            compares = senv.attr.history.compares
            cenvs = {}
            for tenv in TestCase.list_all(penv.branch(), penv.attr.tests.dirs.dm_files):
                TestCase.load_test_text(tenv)
                TestCase.wrap(tenv)
                for compare in compares:
                    cid = compare['history_info']['sha']
                    if cid not in cenvs:
                        cenv = penv.branch()
                        cenvs[cid] = cenv
                        cenv.attr.history.info = compare['history_info']
                        cenv.attr.compare.ref = compare['ref_env'].branch()
                        cenv.attr.compare.prev = compare['base_env'].branch()
                        cenv.attr.compare.next = compare['merge_env'].branch()
                        cenv.attr.compare.report = reports.CompareReport(cenv)
                        senv.attr.repo_report.add_history( cenv )

                    ctenv = cenvs[cid].branch()
                    ctenv.attr.compare.ref = compare['ref_env'].branch()
                    ctenv.attr.compare.prev = compare['base_env'].branch()
                    ctenv.attr.compare.next = compare['merge_env'].branch()
                    Compare.compare_test(ctenv, tenv)
                    senv.attr.repo_report.get_history(cid).attr.compare.report.add_compare_test( ctenv )
        return Shared.Task(env, task, ptags={'action':'history_compare_report'})

    def commit_compare_report(env):
        async def task(penv, senv):
            benv = env.branch()
            base.Byond.Install.load(benv, env.attr.compares.ref_version)

            cenv = penv.branch()
            cenv.attr.compare.ref = benv
            cenv.attr.compare.prev = senv.attr.opendream.commits[senv.attr.git.repo.commit]
            cenv.attr.compare.next = None
            senv.attr.compare.report = reports.CompareReport(cenv)
            for tenv in TestCase.list_all(penv.branch(), penv.attr.tests.dirs.dm_files):
                TestCase.load_test_text(tenv)
                TestCase.wrap(tenv)
                ctenv = cenv.branch()
                ctenv.attr.compare.ref = cenv.attr.compare.ref.branch()
                ctenv.attr.compare.prev = senv.attr.opendream.commits[senv.attr.git.repo.commit].branch()
                ctenv.attr.compare.next = None
                Compare.compare_test(ctenv, tenv)
                senv.attr.compare.report.add_compare_test( ctenv )
        return Shared.Task(env, task, ptags={'action':'commit_compare_report'})

    def write_compare_report(env, name):
        async def task(penv, senv):
            reports.BaseReport.write_report( env.attr.tests.dirs.reports / name, senv.attr.compare.report)
        return Shared.Task(env, task, ptags={'action':'write_report'}, unique=False)

    def write_github_report(env):
        async def task(penv, senv):
            reports.BaseReport.write_report( env.attr.tests.dirs.reports / 'github', senv.attr.repo_report)
        return Shared.Task(env, task, ptags={'action':'write_report'}, unique=False)
    
class OpenDreamRepoResource(Shared.ResourceTracker):
    def __init__(self, env, base_path, limit=None):
        self.env = env
        self.base_path = base_path
        super().__init__(limit=limit)

    def get_resource_data(self, i):
        data = {"id":i, "source_id": f'{self.base_path}.copy.{i}'}
        data["path"] = self.env.attr.opendream.dirs.sources / data["source_id"]
        return data

    def ensure_exist(self, data):
        data["path"].ensure_folder()