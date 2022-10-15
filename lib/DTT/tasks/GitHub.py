
from .common import *

class GitHub(object):
    async def provide_repo(env):
        env.attr.git.remote = 'origin'
        await Shared.Git.Repo.ensure(env)
        Shared.Git.Repo.load(env)
        Shared.Git.Repo.freshen(env)

    ###### commit history ######
    def update_commit_history(env, n=None):
        env = env.branch()
        
        if not Shared.fresh( env.attr.state('history.refresh').get(), minutes=30 ):
            commit_history = env.attr.state('commit_history').get(default={})
            commit_history = Shared.Github.list_all_commits( env, existing_commits=commit_history )        
            env.attr.state('commit_history').set(commit_history)
        else:
            history_state = f'{env.attr.github.repo_id}.history.commits'
            commit_history = env.attr.state('commit_history').get(default={})

        commit_history = sorted( commit_history.values(), key=lambda ch: ch["commit"]["committer"]["date"], reverse=True )
        env.attr.history.infos = commit_history
                

    async def gather_history_commits(env, n=None):
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

        if not Shared.fresh( env.attr.state('pull_requests.refresh').get(), minutes=30 ):
            prs = Shared.Github.list_pull_requests(senv)
            senv.attr.state('pull_requests').set(prs)
        else:
            senv.attr.prs.infos = senv.attr.state('pull_requests').get()

    async def gather_pr_commits(env):
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
