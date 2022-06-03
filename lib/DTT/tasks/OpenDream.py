
from .common import *

from .Install import *
from .Tests import *

class OpenDream(object):
    def source_from_github(env):
        async def task(penv, senv):
            base.OpenDream.Source.from_github(senv)
        return Shared.Task(env, task, tags={'action':'source_from_github'})

    def create_shared_repos(env):
        async def task(penv, senv):
            senv.attr.resources.shared_opendream_repo = OpenDreamRepoResource(env, senv.attr.source.id, limit=4)
            for i in range(0, 4):
                denv = penv.branch()
                base.OpenDream.Source.load(denv, f'{senv.attr.source.id}.copy.{i}')
                await Shared.Path.full_sync_folders(senv, senv.attr.source.dir, denv.attr.source.dir)
            penv.attr.self_task.export( senv, ".resources.shared_opendream_repo" )
        t1 = Shared.Task(env, task, tags={'action':'create_shared_repos'})
        return t1

    async def prepare_build(env):
        await Shared.Path.sync_folders( env, env.attr.source.dir, env.attr.install.dir )
        env.attr.dotnet.solution.path = env.attr.install.dir
        env.attr.resources.opendream_server = Shared.CountedResource(1)

    def build_commit(env):
        async def task(penv, senv):
            try:
                while True:
                    repo = await senv.attr.resources.shared_opendream_repo.acquire()
                    if repo is not None:
                        break
                    await asyncio.sleep(0.2)
                senv.attr.git.repo.local_dir = repo["data"]["path"]
                senv.attr.git.repo.remote = 'origin'
                await Shared.Git.Repo.ensure(senv)
                base.OpenDream.Source.load( senv, repo["data"]["source_id"] )

                await Shared.Git.Repo.ensure_commit(senv)
                await Shared.Git.Repo.command(senv, 'git submodule deinit --all')
                await Shared.Git.Repo.command(senv, 'git clean -fdx')
                await Shared.Git.Repo.init_all_submodules(senv)
                base.OpenDream.Install.from_github(senv)
                await OpenDream.prepare_build(senv)
                await base.OpenDream.Builder.build(senv)
            finally:
                senv.attr.resources.shared_opendream_repo.release(repo)
        return Shared.Task(env, task, tags={'action':'build_commit'} )

    def load_install_from_commit(env, commit):
        env = env.branch()
        Shared.Task.tags(env, {'commit':commit} )
        async def task(penv, senv):
            senv.attr.git.repo.remote_ref = commit
            senv.attr.platform_cls = base.OpenDream
            base.OpenDream.Install.from_github(senv)
            Install.config(senv)
        return Shared.Task(env, task, tags={'action':'load_test_installs'} )

    def build_if_incomplete_tests(env, bottom):
        env = env.branch()
        async def task(penv, senv):
            if len(senv.attr.tests.incomplete) == 0:
                return

            tasks = []
            tasks.append( OpenDream.build_commit(env) )
            tasks.append( Tests.run_incomplete_tests(env) )
            Shared.Task.chain( penv.attr.self_task, *tasks )
            Shared.Task.link_exec( tasks[-1], bottom)
        return Shared.Task(env, task, tags={'action':'build_if_incomplete_tests'} )

    def load_pr_commits(env):
        Shared.Task.tags( env, tags={'commit_type':'pr'} )
        async def task(penv, senv):
            senv.attr.opendream.commits = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs.commits' )
        return Shared.Task(env, task, tags={'action':'load_pr_commits'} )

    def load_history_commits(env, compare_limit):
        env = env.branch()
        Shared.Task.tags( env, tags={'commit_type':'history'} )
        async def task(penv, senv):
            senv.attr.opendream.history_compares = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.history.compares' )
            commits = set()
            compares = []
            for compare in senv.attr.opendream.history_compares:
                if len(commits) >= compare_limit:
                    break
                commits.add( compare['new'] )
                commits.add( compare['base'] )
                compares.append( compare )
            senv.attr.opendream.history_compares = compares
            senv.attr.opendream.commits = commits
        return Shared.Task(env, task, tags={'action':'load_history_commits'} )

    def process_commits(env):
        env = env.branch()
        async def task(penv, senv):
            for commit in senv.attr.opendream.commits:
                tasks = []
                tasks.append( OpenDream.load_install_from_commit(env, commit) )
                tasks.append( Tests.load_incomplete_tests(env, 'default') )
                tasks.append( OpenDream.build_if_incomplete_tests(env, bottom) )
                Shared.Task.chain( t, *tasks )
                Shared.Task.link_exec( tasks[-1], bottom)

        t = Shared.Task(env, task, tags={'action':'process_commits'})
        bottom = Shared.Task.task_group(env, 'process_commits_end')
        Shared.Task.link(t, bottom)
        return Shared.TaskBound(t, bottom)

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