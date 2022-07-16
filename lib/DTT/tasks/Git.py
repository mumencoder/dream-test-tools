
from .common import *

class Git(object):
    ###### utility ######
    def reset_submodule(env):
        async def task(penv, senv):
            await Shared.Git.Repo.command(senv, 'git submodule deinit -f --all')
            #await Shared.Git.Repo.command(senv, 'git clean -fdx')
            await Shared.Git.Repo.init_all_submodules(senv)
        t1 = Shared.Task(env, task, ptags={'action':'clean_commit'})
        return t1

    ###### single commits ######
    def update_head(env):
        async def task(penv, senv):
            await Shared.Git.Repo.freshen(senv)
            senv.attr.git.commits = [ str(senv.attr.git.api.repo.head.commit) ]
        t1 = Shared.Task(env, task, ptags={'action':'update_head'})
        return t1

    ###### commit history ######
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
            senv.attr.history.infos = commit_history
                
        t1 = Shared.Task(env, refresh, ptags={'action':'history_refresh'} ).run_fresh(minutes=30)
        t2 = Shared.Task(env, process, ptags={'action':'history_process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def gather_history_commits(env, n=None):
        async def task(penv, senv):
            senv.attr.history.commits = []
            i = 0
            while i < n:
                prenv = senv.branch()
                prenv.attr.git.commit = senv.attr.history.infos[i]['sha']
                await Shared.Git.Repo.ensure_commit(prenv)
                merge_commit = prenv.attr.git.api.commit

                prenv = senv.branch()
                prenv.attr.git.commit = senv.attr.history.infos[i+1]['sha']
                await Shared.Git.Repo.ensure_commit(prenv)
                base_commit = prenv.attr.git.api.commit

                senv.attr.history.commits.append( {'base': base_commit, 'merge': merge_commit} )

                i += 1

        return Shared.Task(env, task, ptags={'action':'gather_history_commits'})

    def unique_history_commits(env):
        commits = set()
        for pr_commit in env.attr.history.commits:
            commits.add( str(pr_commit['base']) )
            commits.add( str(pr_commit['merge']) )
        return commits

    def find_history_base_commit(env):
        async def task(penv, senv):
            senv.attr.git.commit = Shared.Git.Repo.search_base_commit(senv, senv.attr.git.commit, [info["sha"] for info in senv.attr.history.infos])
            print(senv.attr.git.commit)
        return Shared.Task(env, task, ptags={'action':'get_head_base_history'})

    ###### pull request ######
    def update_pull_requests(env):
        env = env.branch()

        async def refresh(penv, senv):
            penv.attr.state.results.set(f'{senv.attr.github.repo_id}.prs', Shared.Github.list_pull_requests(senv) )
        t1 = Shared.Task(env, refresh, ptags={'action':'pr_refresh'}).run_fresh(minutes=30)

        async def process(penv, senv):
            senv.attr.prs.infos = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs')

        t2 = Shared.Task(env, process, ptags={'action':'pr_process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def gather_pr_commits(env):
        async def task(penv, senv):
            senv.attr.pr.commits = []
            for info in senv.attr.prs.infos:
                prenv = senv.branch()
                prenv.attr.git.commit = info['merge_commit_sha']
                await Shared.Git.Repo.ensure_commit(prenv)
                commit = prenv.attr.git.api.commit
                if len(commit.parents) != 2:
                    raise Exception("expected 2 parent commits from PR sha", commit.parents)
                for c in commit.parents:
                    if str(c) != info["head"]["sha"]:
                        senv.attr.pr.commits.append( {'base': c, 'merge': commit})
        return Shared.Task(env, task, ptags={'action':'gather_pr_commits'})

    def unique_pr_commits(env):
        commits = set()
        for pr_commit in env.attr.pr.commits:
            commits.add( str(pr_commit['base']) )
            commits.add( str(pr_commit['merge']) )
        return commits

    ###### repo resources ######
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
            senv.attr.git.remote = 'origin'
            await Shared.Git.Repo.ensure(senv)

        return Shared.Task(env, task, ptags={'action':'acquire_shared_repo'}, unique=False)

    def release_shared_repo(env):
        async def task(penv, senv):
            senv.attr.shared_repo.source.release(senv.attr.shared_repo.resource)
            penv.attr.self_task.unguard_resource( senv.attr.shared_repo.resource )
        return Shared.Task(env, task, ptags={'action':'release_shared_repo'}, unique=False)