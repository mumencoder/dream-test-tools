
from .common import *

class Git(object):
    def initialize_github(env):
        async def task(penv, senv):
            Shared.Github.prepare(senv)
            for prop in senv.filter_properties('.github.*'):
                penv.attr.self_task.export( senv, prop )
        t1 = Shared.Task(env, task, ptags={'action':'initialize_github'} )
        return t1

    def ensure_repo(env):
        async def task(penv, senv):
            await Shared.Git.Repo.ensure(senv)
            penv.attr.self_task.export(senv, '.git.api.repo')
        t1 = Shared.Task(env, task, ptags={'action':'ensure_repo'})
        return t1

    def freshen_repo(env):
        async def task(penv, senv):
            await Shared.Git.Repo.ensure(senv)
            await Shared.Git.Repo.freshen(senv)
        t1 = Shared.Task(env, task, ptags={'action':'freshen_repo'})
        return t1

    def commit_from_ref(env, ref):
        async def task(penv, senv):
            senv.attr.git.repo.commit = senv.attr.git.api.repo.remote('origin').refs[ref].commit
        return Shared.Task(env, task, ptags={'action':'commit_from_ref'}, stags={'ref':ref})

    def tag_commit(env, commit):
        async def task(penv, senv):
            senv.attr.git.repo.commit = commit
        return Shared.Task(env, task, ptags={'action':'tag_commit'}, stags={'commit':commit})

    def load_clean_commit(env):
        async def task(penv, senv):
            await Shared.Git.Repo.command(senv, 'git submodule deinit --all')
            await Shared.Git.Repo.command(senv, 'git clean -fdx')
            await Shared.Git.Repo.ensure_commit(senv)
            await Shared.Git.Repo.init_all_submodules(senv)
        t1 = Shared.Task(env, task, ptags={'action':'load_clean_commit'})
        return t1

    def update_commit_history(env, n=None):
        env = env.branch()

        async def refresh(penv, senv):
            history_state = f'{senv.attr.github.repo_id}.history.commits'
            commit_history = penv.attr.state.results.get(history_state, default={})
            commit_history = Shared.Github.list_all_commits( senv, existing_commits=commit_history )        
            penv.attr.state.results.set(history_state, commit_history)

        async def process(penv, senv):
            history_state = f'{senv.attr.github.repo_id}.history.commits'
            commit_history = penv.attr.state.results.get(history_state, default={})
            commit_history = sorted( commit_history.values(), key=lambda ch: ch["commit"]["committer"]["date"], reverse=True )
            senv.attr.git.commits = [ch["commit"]["sha"] for ch in commit_history.values()]
            senv.attr.history.infos = commit_history
            if n is not None:
                senv.attr.history.truncated_infos = senv.attr.history.infos[0:n]
                
        t1 = Shared.Task(env, refresh, ptags={'action':'history_refresh'} ).run_fresh(minutes=30)
        t2 = Shared.Task(env, process, ptags={'action':'history_process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def tag_history(env, history):
        async def task(penv, senv):
            senv.attr.history.info = history
        return Shared.Task(env, task, ptags={'action':'tag_history'}, stags={'history':history["sha"]})

    def load_history(env):
        async def task(penv, senv):
            senv.attr.git.repo.commit = senv.attr.history.info["sha"]
            await Shared.Git.Repo.ensure_commit(senv)
        return Shared.Task(env, task, ptags={'action':'load_history'})

    def update_pull_requests(env):
        env = env.branch()

        async def refresh(penv, senv):
            penv.attr.state.results.set(f'{senv.attr.github.repo_id}.prs', Shared.Github.list_pull_requests(senv) )
        t1 = Shared.Task(env, refresh, ptags={'action':'pr_refresh'}).run_fresh(minutes=30)

        async def process(penv, senv):
            senv.attr.prs.infos = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs')
            senv.attr.git.commits = [ info['merge_commit_sha'] for info in senv.attr.prs.infos ]
        t2 = Shared.Task(env, process, ptags={'action':'pr_process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def fetch_commits(env):
        async def task(penv, senv):
            for commit in senv.attr.git.commits:
                senv.attr.git.repo.commit = commit
                await Shared.Git.Repo.ensure_commit(senv)
        return Shared.Task(env, task, ptags={'action':'fetch_commits'})

    def tag_pull_request(env, pull_info):
        async def task(penv, senv):
            senv.attr.pr.info = pull_info
        return Shared.Task(env, task, ptags={'action':'tag_pull_request'}, stags={'pr_id':pull_info["id"]})

    def load_pull_request(env):
        async def task(penv, senv):
            prenv = senv.branch()
            prenv.attr.git.repo.commit = senv.attr.pr.info['merge_commit_sha']
            await Shared.Git.Repo.ensure_commit(prenv)
            if len(prenv.attr.git.api.repo.head.commit.parents) != 2:
                raise Exception("expected 2 parent commits from PR sha", prenv.attr.git.api.repo.head.commit.parents)
            for c in prenv.attr.git.api.repo.head.commit.parents:
                if str(c) != senv.attr.pr.info["head"]["sha"]:
                    senv.attr.pr.merge_commit = str(prenv.attr.git.repo.commit)
                    senv.attr.pr.base_commit = str(c)
            
        return Shared.Task(env, task, ptags={'action':'load_pull_request'})

    class RepoSource(Shared.ResourceTracker):
        def __init__(self, env, base_dir, base_name, limit=None):
            self.env = env
            self.base_dir = base_dir
            self.base_name = base_name
            super().__init__(limit=limit)

        def get_resource_data(self, i):
            data = {"id":i, "copy_name": f'{self.base_name}.copy.{i}'}
            data["path"] = self.base_dir / data["copy_name"]
            return data

        def ensure_exist(self, data):
            data["path"].ensure_folder()

    def create_shared_repos(env):
        async def task(penv, senv):
            senv.attr.shared_repo.source = Git.RepoSource(env, 
                senv.attr.shared_repo.root_dir, 
                senv.attr.shared_repo.name,
                limit=senv.attr.shared_repo.limit)
            for i in range(0, senv.attr.shared_repo.limit):
                res = senv.attr.shared_repo.source.get_resource_data(i)
                await Shared.Path.full_sync_folders(senv, senv.attr.git.repo.local_dir, res['path'])
            penv.attr.self_task.export( senv, ".shared_repo.source" )
        t1 = Shared.Task(env, task, ptags={'action':'create_shared_repos'})
        return t1

    def acquire_shared_repo(env):
        async def task(penv, senv):
            while True:
                repo = await senv.attr.shared_repo.source.acquire()
                if repo is not None:
                    break
                await asyncio.sleep(0.1)
            senv.attr.shared_repo.resource = repo
            penv.attr.self_task.guard_resource( senv.attr.shared_repo.source, repo )
            senv.attr.git.repo.local_dir = repo["data"]["path"]
            senv.attr.git.repo.remote = 'origin'
            await Shared.Git.Repo.ensure(senv)

        return Shared.Task(env, task, ptags={'action':'acquire_shared_repo'}, unique=False)

    def release_shared_repo(env):
        async def task(penv, senv):
            senv.attr.shared_repo.source.release(senv.attr.shared_repo.resource)
            penv.attr.self_task.unguard_resource( senv.attr.shared_repo.resource )
        return Shared.Task(env, task, ptags={'action':'release_shared_repo'}, unique=False)