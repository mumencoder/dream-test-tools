
from .common import *

from .Install import *
from .Tests import *
from .Git import *
from .Compare import *
from .TestCase import *

class OpenDream(object):
    class Setup(object):
        def metadata(env):
            env.attr.opendream.processed_commits = Shared.AtomicSet()
            env.attr.opendream.commits = {}
            env.attr.opendream.installs = {}

        def shared_repos(env):
            tasks = []
            tasks.append( Git.freshen_repo(env).run_fresh(minutes=30) )
            tasks.append( Git.create_shared_repos(env) )
            env.attr.named_tasks["OpenDream.shared_repos"] = tasks[-1]
            return Shared.Task.bounded_tasks( *tasks )

        def github(env):
            tasks = []
            tasks.append( Git.initialize_github(env) )
            tasks.append( OpenDream.source_from_github(env) )
            tasks.append( Git.ensure_repo(env) )
            tasks.append( OpenDream.initialize_github_compares(env) )
            env.attr.named_tasks["OpenDream.github"] = tasks[-1]
            return Shared.Task.bounded_tasks( *tasks )
        
        def reports(env):
            task = OpenDream.write_github_report(env)
            Shared.Task.link( env.attr.named_tasks['pr.finish'], task, ltype="exec" )
            Shared.Task.link( env.attr.named_tasks['history.finish'], task, ltype="exec" )
            return task

        def update_pull_requests(env):
            tasks = [ ]
            tasks.append( Shared.Task.group(env, 'OpenDream.update_pull_requests') )
            tasks.append( Git.update_pull_requests(env) )
            tasks.append( Git.fetch_commits(env) )
            return Shared.Task.bounded_tasks( *tasks )

        def process_pull_requests(env):
            tasks = [ ]
            subtasks = lambda env, pull_info: Shared.Task.bounded_tasks(
                Git.tag_pull_request( env, pull_info ),
                Git.acquire_shared_repo( env ),
                Git.load_pull_request( env ),
                Git.release_shared_repo( env ),
                OpenDream.process_pr_commits( env, lambda: OpenDream.commit_tasks(env) ),
                OpenDream.load_pr_compare( env )
            )
            tasks.append( Shared.Task.subtask_source(env.branch(), '.prs.infos', subtasks, limit=4, tags={'action':'pr_subtasks'}) )
            tasks.append( OpenDream.pr_compare_report( env ) )
            env.attr.named_tasks['OpenDream.update_pr'] = tasks[-1]

            Shared.Task.link( env.attr.named_tasks["OpenDream.github"], tasks[0], ltype=["tag", "import"] )
            return Shared.Task.bounded_tasks( *tasks )

        def truncate_history(env, n):
            pass

        def update_commit_history(env):
            tasks = [ ]
            tasks.append( Shared.Task.group(env, 'OpenDream.update_commit_history') )
            tasks.append( Git.update_commit_history(env) )
            tasks.append( Git.fetch_commits(env) )
            return Shared.Task.bounded_tasks( *tasks )

        def process_commit_history(env):
            subtasks = lambda env, history_info: Shared.Task.bounded_tasks(
                Git.tag_history( env, history_info ),
                Git.acquire_shared_repo( env ),
                Git.load_history( env ),
                Git.release_shared_repo( env ),
                OpenDream.process_history_commit( env, lambda: env.commit_tasks(env) ),
            )
            tasks = []
            tasks.append( Shared.Task.subtask_source(env.branch(), '.history.truncated_infos', subtasks, limit=4, tags={'action':'history_subtasks'}) )
            tasks.append( OpenDream.load_history_compares( env ) )
            tasks.append( OpenDream.history_compare_report( env ) )
            env.attr.named_tasks['history.finish'] = tasks[-1]

            Shared.Task.link( env.attr.named_tasks["OpenDream.github"], tasks[0], ltype=["tag", "import"] )
            return Shared.Task.bounded_tasks( *tasks )
            
        ### main branch HEAD test
        def test_main_branch(env):
            tasks = []
            tasks.append( Shared.Task.group(env, 'test_main_branch') )
            tasks.append( Tests.load_tests(env, 'default') )
            tasks.append( Git.commit_from_ref(env, "HEAD") )
            tasks.append( OpenDream.acquire_shared_repo( env ) )
            tasks.append( Git.load_clean_commit(env) )
            tasks.append( OpenDream.load_install_from_github(env) )
            tasks.append( OpenDream.commit_tasks(env) )
            tasks.append( OpenDream.release_shared_repo( env ) )
            tasks.append( OpenDream.commit_compare_report( env ) )
            tasks.append( OpenDream.write_compare_report(env, 'main') )
            Shared.Task.chain( env.attr.scheduler.top_task, *tasks )
            Shared.Task.link( env.attr.named_tasks["init_github"], tasks[0], ltype=["tag", "import"] )
            Shared.Task.link( env.attr.named_tasks["shared_repos"], tasks[0], ltype="import" )
            Shared.Task.link( env.attr.named_tasks["ensure_repo"], tasks[0], ltype="import" )

        def update_local(self, local_name, local_dir):
            tasks = []
            tasks.append( Shared.Task.group(env, 'update_local') )
            tasks.append( OpenDream.load_install_from_local(env, local_name, local_dir) )
            env.attr.named_tasks["local.copy"] = tasks[-1]
            tasks.append( OpenDream.build_local(env) )
            tasks.append( Tests.clear_tests(env, 'default') )
            tasks.append( Tests.load_incomplete_tests(env, 'default') )
            tasks.append( Tests.run_incomplete_tests(env) )

            Shared.Task.chain( env.attr.named_tasks["init_github"], *tasks)

    ############### Begin tasks ##############
    def source_from_github(env):
        async def task(penv, senv):
            base.OpenDream.Source.load(senv, f'github.{senv.attr.github.repo_id}.{senv.attr.github.tag}')
            senv.attr.git.repo.local_dir = senv.attr.source.dir
            senv.attr.shared_repo.limit = 4
            senv.attr.shared_repo.root_dir = env.attr.opendream.dirs.sources
            senv.attr.shared_repo.name = senv.attr.opendream.source.id

        return Shared.Task(env, task, ptags={'action':'source_from_github'})

    def source_from_shared(env):
        async def task(penv, senv):
            base.OpenDream.Source.load(senv, senv.attr.shared_repo.resource["data"]["copy_name"] )
        return Shared.Task(env, task, ptags={'action':'source_from_shared'})

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
        return Shared.Task(env, task, ptags={'action':'load_install_from_github'}, tagfn=process_tags )

    def wait_for_commit(env, commit_id):
        async def task(penv, senv):
            while commit_id not in penv.attr.opendream.commits:
                await asyncio.sleep(0.5)
        return Shared.Task(env, task, ptags={'action':'wait_for_commit', 'commit_id':commit_id}, unique=False )
        
    def process_pr_commits(env, process_task):
        async def task(penv, senv):
            if await penv.attr.opendream.processed_commits.check_add( senv.attr.pr.base_commit ) is False:
                base_tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.pr.base_commit), 
                    Git.acquire_shared_repo( env ),
                    OpenDream.source_from_shared(env),
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task(),
                    Git.release_shared_repo( env )
                )
                Shared.Task.link( penv.attr.self_task, base_tasks ) 
                Shared.Task.link( base_tasks, bottom, ltype="exec" )
            else:
                task = OpenDream.wait_for_commit( env, senv.attr.pr.base_commit)
                Shared.Task.link( penv.attr.self_task, task )
                Shared.Task.link( task, bottom, ltype="exec")
            if await penv.attr.opendream.processed_commits.check_add( senv.attr.pr.merge_commit ) is False:
                # TODO: better way to do this
                if senv.attr.pr.info['id'] == 748018792:
                    extra_task = Shared.Task.set_senv(env, '.compilation.args', {'flags':['experimental-preproc']})
                else:
                    extra_task = Shared.Task.nop(env)

                merge_tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.pr.merge_commit), 
                    extra_task,
                    Git.acquire_shared_repo( env ),
                    OpenDream.source_from_shared(env),
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task(),
                    Git.release_shared_repo( env ) 
                )
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
            if await penv.attr.opendream.processed_commits.check_add( senv.attr.git.repo.commit ) is False:
                tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.git.repo.commit), 
                    OpenDream.acquire_shared_repo( env ),
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task(),
                    OpenDream.release_shared_repo( env ) 
                )
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

    def commit_tasks(env):
        return Shared.Task.bounded_tasks( 
            Tests.load_tests(env, 'default'),
            OpenDream.process_commit(env), 
            Tests.run_tests(env),
            Tests.save_complete_tests( env )
        )

    def process_commit(env):
        def no_incomplete_tests(penv, senv):
            return len(senv.attr.tests.incomplete) == 0

        async def task(penv, senv):
            penv.attr.opendream.commits[ senv.attr.git.repo.commit ] = senv
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
            base.Byond.Install.load(benv, env.attr.byond.install.version)
            compare = {'pull_info': senv.attr.pr.info,
                'ref_env':benv, 
                'base_env':penv.attr.opendream.commits[senv.attr.pr.base_commit], 
                'merge_env':penv.attr.opendream.commits[senv.attr.pr.merge_commit]
            }
            senv.attr.pr.compares.append(compare)
        return Shared.Task(env, task, ptags={'action':'load_pr_compare'})

    def load_history_compares(env):
        async def task(penv, senv):
            i = 0
            while i+1 < len(senv.attr.history.truncated_infos):
                merge_info = senv.attr.history.truncated_infos[i]
                base_info = senv.attr.history.truncated_infos[i+1]

                benv = env.branch()
                base.Byond.Install.load(benv, env.attr.byond.install.version)
                compare = {'history_info': merge_info,
                    'ref_env':benv, 
                    'base_env':penv.attr.opendream.commits[base_info["sha"]], 
                    'merge_env':penv.attr.opendream.commits[merge_info["sha"]]
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
            base.Byond.Install.load(benv, env.attr.byond.install.version)

            cenv = penv.branch()
            cenv.attr.compare.ref = benv
            cenv.attr.compare.prev = penv.attr.opendream.commits[senv.attr.git.repo.commit]
            cenv.attr.compare.next = None
            senv.attr.compare.report = reports.CompareReport(cenv)
            for tenv in TestCase.list_all(penv.branch(), penv.attr.tests.dirs.dm_files):
                TestCase.load_test_text(tenv)
                TestCase.wrap(tenv)
                ctenv = cenv.branch()
                ctenv.attr.compare.ref = cenv.attr.compare.ref.branch()
                ctenv.attr.compare.prev = penv.attr.opendream.commits[senv.attr.git.repo.commit].branch()
                ctenv.attr.compare.next = None
                Compare.compare_test(ctenv, tenv)
                senv.attr.compare.report.add_compare_test( ctenv )
        return Shared.Task(env, task, ptags={'action':'commit_compare_report'})

    def write_compare_report(env, name):
        async def task(penv, senv):
            report_dir = env.attr.tests.dirs.reports / name
            shutil.rmtree( report_dir )
            reports.BaseReport.write_report( env.attr.tests.dirs.reports / name, senv.attr.compare.report)
        return Shared.Task(env, task, ptags={'action':'write_report'}, unique=False)

    def write_github_report(env):
        async def task(penv, senv):
            report_dir = env.attr.tests.dirs.reports / 'github'
            shutil.rmtree( report_dir )
            reports.BaseReport.write_report( report_dir, senv.attr.repo_report)
        return Shared.Task(env, task, ptags={'action':'write_report'}, unique=False)