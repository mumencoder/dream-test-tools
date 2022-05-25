
from .common import *

class UpdateApp(object):
    async def get_weekly_commits(self, env):
        uenv = env.branch()

        repo = uenv.attr.git.api.repo
        commit = repo.commit('origin/HEAD')
        commits = Shared.Git.weekly_builds( Shared.Git.Repo.commit_history(commit, depth=1024) )
        i = 0
        while i < len(commits) - 2:
            benv = uenv.branch()
            benv.attr.new_commit = commits[i]
            benv.attr.previous_commit = commits[i+1]
            benv.attr.git.repo.remote = 'origin'
            benv.attr.git.repo.remote_ref = str(benv.attr.new_commit)
            benv.attr.source.id = f'github.{benv.attr.github.repo_id}.{str(benv.attr.new_commit)}'
            yield benv
            i += 1

    async def get_recent_commits(self, env):
        uenv = env.branch()

        repo = uenv.attr.git.api.repo
        commit = repo.commit('origin/HEAD')
        commits = list(Shared.Git.Repo.commit_history(commit, depth=16))
        i = 0
        while i < len(commits) - 2:
            benv = uenv.branch()
            benv.attr.new_commit = commits[i]
            benv.attr.previous_commit = commits[i+1]
            Shared.Workflow.set_task(benv, self.build_opendream_history(benv))
            yield benv

            i += 1