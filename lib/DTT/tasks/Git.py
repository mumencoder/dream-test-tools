
from .common import *

class Git(object):
    def initialize_github(env, owner, repo, tag):
        Shared.Task.tags(env, {'github.owner':owner, 'github.repo':repo, 'github.tag':tag} )
        async def task(penv, senv):
            senv.attr.github.owner = owner
            senv.attr.github.repo = repo
            senv.attr.github.tag = tag
            Shared.Github.prepare(senv)
        t1 = Shared.Task(env, task, tags={'action':'initialize_github'})
        return t1

    def freshen_repo(env):
        async def task(penv, senv):
            await Shared.Git.Repo.ensure(senv)
            await Shared.Git.Repo.freshen(senv)
            await Shared.Git.Repo.init_all_submodules(senv)
        t1 = Shared.Task(env, task, tags={'action':'freshen_repo'}).run_fresh(minutes=30)
        return t1

    def update_commit_history(env):
        env = env.branch()

        async def refresh(penv, senv):
            history_state = f'{senv.attr.github.repo_id}.history.commits'
            compare_state = f'{senv.attr.github.repo_id}.history.compares'
            commit_history = penv.attr.state.results.get(history_state, default={})
            commit_history = Shared.Github.list_all_commits( senv, existing_commits=commit_history )        
            penv.attr.state.results.set(history_state, commit_history)

        async def process(penv, senv):
            history_state = f'{senv.attr.github.repo_id}.history.commits'
            compare_state = f'{senv.attr.github.repo_id}.history.compares'
            commit_history = penv.attr.state.results.get(history_state)
            commits = sorted( commit_history.keys(), key=lambda k: commit_history[k]["commit"]["committer"]["date"], reverse=True )
            compare_commits = []
            for i, commit in enumerate(commits):
                if i+1 == len(commits):
                    continue
                compare_commits.append( {"commit_info":commit_history[commits[i]], "base":commits[i+1], "new":commits[i]} )
            penv.attr.state.results.set(compare_state, compare_commits)

        t1 = Shared.Task(env, refresh, tags={'action':'refresh'} ).run_fresh(minutes=30)
        t2 = Shared.Task(env, process, tags={'action':'process'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def update_pull_requests(env):
        env = env.branch()

        async def refresh_pull_requests(penv, senv):
            penv.attr.state.results.set(f'{senv.attr.github.repo_id}.prs', Shared.Github.list_pull_requests(senv) )
        t1 = Shared.Task(env, refresh_pull_requests, tags={'action':'refresh_pull_requests'}).run_fresh(minutes=30)

        async def process_pull_requests(penv, senv):
            prs = penv.attr.state.results.get(f'{senv.attr.github.repo_id}.prs')
            commits = set()
            compare_commits = []

            try:
                while True:
                    repo = await senv.attr.resources.shared_opendream_repo.acquire()
                    if repo is not None:
                        break
                    await asyncio.sleep(0.2)
                renv = penv.branch()
                renv.attr.git.repo.local_dir = repo["data"]["path"]
                renv.attr.git.repo.remote = 'origin'
                await Shared.Git.Repo.ensure(renv)

                for pull_info in prs:
                    prenv = renv.branch()
                    prenv.attr.pull_info = pull_info

                    pr_commit = pull_info['merge_commit_sha']
                    prenv.attr.git.repo.commit = pr_commit
                    await Shared.Git.Repo.ensure_commit(prenv)
                    if len(prenv.attr.git.api.repo.head.commit.parents) != 2:
                        raise Exception("expected 2 parent commits from PR sha", prenv.attr.git.api.repo.head.commit.parents)
                    for c in prenv.attr.git.api.repo.head.commit.parents:
                        if str(c) != pull_info["head"]["sha"]:
                            base_commit = str(c)

                    commits.add(base_commit)
                    commits.add(pr_commit)
                    compare_commits.append( {"pull_info":pull_info, "base":base_commit, "pr":pr_commit} )
            finally:
                senv.attr.resources.shared_opendream_repo.release(repo)

            penv.attr.state.results.set(f'{senv.attr.github.repo_id}.prs.commits', list(commits) )
            penv.attr.state.results.set(f'{senv.attr.github.repo_id}.prs.compare_commits', list(compare_commits) )
        t2 = Shared.Task(env, process_pull_requests, tags={'action':'process_pull_requests'})

        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)
