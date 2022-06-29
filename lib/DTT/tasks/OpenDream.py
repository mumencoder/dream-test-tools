
from .common import *

from .Install import *
from .Tests import *
from .Git import *

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

    def build(env):
        async def task(penv, senv):
            await OpenDream.prepare_build(senv)
            await base.OpenDream.Builder.build(senv)
        return Shared.Task(env, task, ptags={'action':'build'} )

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

    def process_pr_commits(env, process_task):
        async def task(penv, senv):
            await senv.send_event("pr_commits", senv)
            if await senv.attr.opendream.processed_commits.check_add( senv.attr.pr.merge_commit ) is False:
                merge_tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.pr.merge_commit), 
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task() )
                Shared.Task.link( penv.attr.self_task, merge_tasks )
                Shared.Task.link_exec( merge_tasks, bottom )
            if await senv.attr.opendream.processed_commits.check_add( senv.attr.pr.base_commit ) is False:
                base_tasks = Shared.Task.bounded_tasks( 
                    Git.tag_commit(env, senv.attr.pr.base_commit), 
                    Git.load_clean_commit(env), 
                    OpenDream.load_install_from_github(env),
                    process_task() )
                Shared.Task.link( penv.attr.self_task, base_tasks ) 
                Shared.Task.link_exec( base_tasks, bottom )

        top = Shared.Task(env, task, ptags={'action':'process_pr_commits'} )
        bottom = Shared.Task.group(env, 'process_pr_commits_end')
        Shared.Task.link( top, bottom )
        return Shared.TaskBound(top, bottom)

    def process_commit(env):
        env = env.branch()

        def no_incomplete_tests(penv, senv):
            return len(senv.attr.tests.incomplete) == 0

        async def task(penv, senv):
            await senv.send_event("commit_install", senv)
            if no_incomplete_tests(penv, senv):
                penv.attr.self_task.halt()
                return

            await OpenDream.prepare_build(senv)
            await base.OpenDream.Builder.build(senv)

            if not base.OpenDream.Builder.build_ready(senv):
                penv.attr.self_task.halt()

        return Shared.Task(env, task, ptags={'action':'process_commit'})

    def load_pr_compares(env):
        async def task(penv, senv):
            senv.attr.compares = []
            for (base_commit, merge_commit), info in senv.attr.opendream.pr.commits.values():
                benv = senv.branch()
                Byond.Install.load(benv, self.byond_ref_version)
                compare = {'ref':benv, 'base_env':info[base_commit]["env"], 'merge_env':info[merge_commit]["env"]}
                senv.attr.compares.append(compare)
        return Shared.Task(env, task, ptags={'action':'load_pr_compares'})

    async def prepare_build(env):
        await Shared.Path.sync_folders( env, env.attr.source.dir, env.attr.install.dir )
        env.attr.dotnet.solution.path = env.attr.install.dir
        env.attr.resources.opendream_server = Shared.CountedResource(1)

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

async def OD_compares():
    commits = {}
    compares = []

    if base_commit not in commits:
        commits[base_commit] = senv.branch()
    if pr_commit not in commits:
        commits[pr_commit] = senv.branch()
        if pull_info['id'] == 748018792:
            commits[pr_commit].attr.compilation.args = {'flags':['experimental-preproc']}

    compares.append( {"type":"pr", "pull_info":pull_info, "base":base_commit, "new":pr_commit} )

    senv.attr.git.commits = commits
    senv.attr.opendream.compares = compares

