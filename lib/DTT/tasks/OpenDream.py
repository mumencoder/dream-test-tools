
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

    async def run_build_commit(env):
        await Shared.Git.Repo.ensure_commit(env)
        await Shared.Git.Repo.command(env, 'git submodule deinit --all')
        await Shared.Git.Repo.command(env, 'git clean -fdx')
        await Shared.Git.Repo.init_all_submodules(env)
        await OpenDream.prepare_build(env)
        await base.OpenDream.Builder.build(env)

    def build_commit_shared(env):
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

                await OpenDream.run_build_commit(senv)
            finally:
                senv.attr.resources.shared_opendream_repo.release(repo)
        return Shared.Task(env, task, tags={'action':'build_commit'} )

    def build_local(env):
        async def task(penv, senv):
            await OpenDream.prepare_build(senv)
            await base.OpenDream.Builder.build(senv)
        return Shared.Task(env, task, tags={'action':'build_local'} )

    def load_install_from_local(env, local_name, local_dir):
        env = env.branch()
        Shared.Task.tags(env, {'local_name':local_name} )
        async def task(penv, senv):
            senv.attr.source.dir = local_dir
            senv.attr.git.repo.local_dir = local_dir
            Shared.Git.Repo.load(senv)
            base.OpenDream.Install.load(senv, f'local.{local_name}')
            senv.attr.platform_cls = base.OpenDream
            Install.config(senv)
        return Shared.Task(env, task, tags={'action':'load_install_from_local'} )

    def load_install_from_github(env, commit, remote=None):
        env = env.branch()
        Shared.Task.tags(env, {'commit':commit} )
        async def task(penv, senv):
            senv.attr.git.repo.remote = 'origin'
            senv.attr.git.repo.commit = commit
            senv.attr.platform_cls = base.OpenDream
            base.OpenDream.Install.from_github(senv)
            Install.config(senv)
        return Shared.Task(env, task, tags={'action':'load_install_from_github'} )

    def load_pr_commits(env):
        Shared.Task.tags( env, tags={'commit_type':'pr'} )
        async def task(penv, senv):
            commit_tasks = []
            commits = set(penv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs.commits' ))
            compares = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs.compares' )
            new_compares = []
            for commit in commits:
                commit_tasks.append( OpenDream.load_install_from_github(env, commit) )
            for compare in compares:
                cenv_new = senv.branch()
                cenv_new.attr.git.repo.commit = compare['new']
                base.OpenDream.Install.from_github(cenv_new) 

                cenv_base = senv.branch()
                cenv_base.attr.git.repo.commit = compare['base']
                base.OpenDream.Install.from_github(cenv_base) 

                compare["cenv_new"] = cenv_new
                compare["cenv_base"] = cenv_base
                new_compares.append( compare )
            senv.attr.opendream.compares = new_compares
            senv.attr.opendream.commit_tasks = commit_tasks
            senv.attr.opendream.commits = commits
        return Shared.Task(env, task, tags={'action':'load_pr_commits'} )

    def load_history_commits(env, compare_limit):
        env = env.branch()
        Shared.Task.tags( env, tags={'commit_type':'history'} )
        async def task(penv, senv):
            commits = set()
            compares = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.history.compares' )
            new_compares = []
            for compare in compares:
                if len(commits) >= compare_limit:
                    break
                commits.add( compare['new'] )
                commits.add( compare['base'] )

                cenv_new = senv.branch()
                cenv_new.attr.git.repo.commit = compare['new']
                base.OpenDream.Install.from_github(cenv_new) 

                cenv_base = senv.branch()
                cenv_base.attr.git.repo.commit = compare['base']
                base.OpenDream.Install.from_github(cenv_base) 

                compare["cenv_new"] = cenv_new
                compare["cenv_base"] = cenv_base
                new_compares.append( compare )
            commit_tasks = []
            for commit in commits:
                commit_tasks.append( OpenDream.load_install_from_github(env, commit) )
            senv.attr.opendream.compares = new_compares
            senv.attr.opendream.commit_tasks = commit_tasks
            senv.attr.opendream.commits = commits
        return Shared.Task(env, task, tags={'action':'load_history_commits'} )

    def set_commit_tasks(env, commit_tasks):
        env = env.branch()
        Shared.Task.tags( env, tags={'commit_type':'general'} )
        async def task(penv, senv):
            senv.attr.opendream.commit_tasks = commit_tasks
        return Shared.Task(env, task, tags={'action':'set_commit_tasks'} )

    def process_commits(env):
        env = env.branch()

        def no_incomplete_tests(penv, senv):
            return len(senv.attr.tests.incomplete) == 0

        def build_failure(penv, senv):
            if len( base.OpenDream.Compilation.get_exe_path(senv) ) != 1:
                return True
            if len( base.OpenDream.Run.get_exe_path(senv) ) != 1:
                return True
            return False

        async def task(penv, senv):
            for commit_task in senv.attr.opendream.commit_tasks:
                tasks = []
                tasks.append( commit_task )
                tasks.append( Tests.load_incomplete_tests(env, 'default') )
                tasks.append( Shared.Task.halt_on_condition(env, no_incomplete_tests, "1" ) )
                tasks.append( OpenDream.build_commit_shared(env) )
                tasks.append( Shared.Task.halt_on_condition(env, build_failure, "2"))
                tasks.append( Tests.run_incomplete_tests(env) )
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