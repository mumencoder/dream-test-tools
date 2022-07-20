
from .common import *

class GitHub(object):
    class Target(object):
        def load_pull_requests(env):
            if not env.attr_exists('.target.pull_request'):
                env.attr.target.pull_request = Shared.Target( Git.update_pull_requests(env) )
                Shared.Task.link( env.attr.target.load_github(), env.attr.target.pull_request )
            return env.attr.target.pull_request

        def load_commit_historys(env):
            if not env.attr_exists('.target.commit_history'):
                env.attr.target.commit_history = DTT.tasks.Git.update_commit_history(env)
                Shared.Task.link( env.attr.target.load_github(), env.attr.target.commit_history )
            return env.attr.target.commit_history

    def provide_repo(env):
        env.attr.git.remote = 'origin'
        await Shared.Git.Repo.ensure(env)
        Shared.Git.Repo.load(env)
        Shared.Git.Repo.freshen(env)

    ###### commit history ######
    def update_commit_history(env, n=None):
        env = env.branch()

        async def refresh(senv):
            history_state = f'{senv.attr.github.repo_id}.history.commits'
            commit_history = senv.attr.state.results.get(history_state, default={})
            commit_history = Shared.Github.list_all_commits( senv, existing_commits=commit_history )        
            senv.attr.state.results.set(history_state, commit_history)

        async def process(senv):
            history_state = f'{senv.attr.github.repo_id}.history.commits'
            commit_history = senv.attr.state.results.get(history_state, default={})
            commit_history = sorted( commit_history.values(), key=lambda ch: ch["commit"]["committer"]["date"], reverse=True )
            senv.attr.history.infos = commit_history
                
        t1 = Shared.Task(env, refresh, ptags={'action':'history_refresh'} ).run_fresh(minutes=30)
        t2 = Shared.Task(env, process, ptags={'action':'history_process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def gather_history_commits(env, n=None):
        env.attr.history.commits = []
        i = 0
        while i < n:
            prenv = env.branch()
            prenv.attr.git.commit = env.attr.history.infos[i]['sha']
            await Shared.Git.Repo.ensure_commit(prenv)
            merge_commit = prenv.attr.git.api.commit

            prenv = env.branch()
            prenv.attr.git.commit = env.attr.history.infos[i+1]['sha']
            await Shared.Git.Repo.ensure_commit(prenv)
            base_commit = prenv.attr.git.api.commit

            env.attr.history.commits.append( {'base': base_commit, 'merge': merge_commit} )

            i += 1

    def unique_history_commits(env):
        commits = set()
        for infos in env.attr.history.infos:
            commits.add( infos['sha'] )
        return commits

    def find_history_base_commit(env):
        commits = [info["sha"] for info in env.attr.history.infos]
        env.attr.git.commit = Shared.Git.Repo.search_base_commit(env, env.attr.git.commit, commits)

    ###### pull request ######
    def update_pull_requests(env):
        env = env.branch()

        async def refresh(senv):
            senv.attr.state.results.set(f'{senv.attr.github.repo_id}.prs', Shared.Github.list_pull_requests(senv) )
        t1 = Shared.Task(env, refresh, ptags={'action':'pr_refresh'}).run_fresh(minutes=30)

        async def process(senv):
            senv.attr.prs.infos = senv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs')

        t2 = Shared.Task(env, process, ptags={'action':'pr_process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def gather_pr_commits(env):
        env.attr.pr.commits = []
        for info in env.attr.prs.infos:
            prenv = env.branch()
            prenv.attr.git.commit = info['merge_commit_sha']
            await Shared.Git.Repo.ensure_commit(prenv)
            commit = prenv.attr.git.api.commit
            if len(commit.parents) != 2:
                raise Exception("expected 2 parent commits from PR sha", commit.parents)
            for c in commit.parents:
                if str(c) != info["head"]["sha"]:
                    env.attr.pr.commits.append( {'base': c, 'merge': commit})

    def unique_pr_commits(env):
        commits = set()
        for pr_commit in env.attr.pr.commits:
            commits.add( str(pr_commit['base']) )
            commits.add( str(pr_commit['merge']) )
        return commits
