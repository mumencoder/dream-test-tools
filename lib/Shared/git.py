import os, subprocess
import collections
import asyncio
import git

import Shared

class Git(object):
    class AutoStash(object):
        async def __enter__(self):
            await Git.Repo.command(env, "git stash")

        async def __exit__(self, exc_type, exc_value, exc_traceback):
            await Git.Repo.command(env, "git stash pop")

    @staticmethod
    def nightly_builds(commits):
        nights = collections.defaultdict(list)
        for commit in commits:
            h = tuple( [getattr(commit.committed_datetime, attr) for attr in ["year", "month", "day"]] )
            nights[h].append( commit )
        return [max(commits, key=lambda c: c.committed_date) for commits in nights.values()]

    class Repo(object):
        @staticmethod 
        def commit_history(commit, depth=32):
            q = []
            seen = set()
            i = 0
            while i < depth:
                yield commit
                for c in commit.parents:
                    if c not in seen:
                        seen.add(c)
                        i += 1
                        q.append(c)
                commit = q.pop(0)

        @staticmethod
        async def command(env, command):
            env = env.branch()
            env.attr.shell.dir = env.attr.git.repo.local_dir
            env.attr.shell.command = command
            await Shared.Process.shell(env)

        @staticmethod
        def exists(env):
            if not os.path.exists(env.attr.git.repo.local_dir):
                os.mkdir( env.attr.git.repo.local_dir )
            with Shared.folder.Push(env.attr.git.repo.local_dir):
                process = subprocess.run('git status', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                if process.returncode == 0:
                    return True
                else:
                    return False

        @staticmethod
        async def ensure(env):
            if not Git.Repo.exists(env):
                with Shared.Workflow.status(env, "waiting git"):
                    try:
                        await env.attr.resources.git.acquire(env)
                        env.attr.shell.command = f"git clone --depth {env.attr.git.repo.clone_depth} --branch {env.attr.git.repo.branch['name']} {env.attr.git.repo.url} {env.attr.git.repo.local_dir}"
                        env.attr.wf.status[-1] = "git clone"
                        await Shared.Process.shell(env)
                    finally:
                        env.attr.resources.git.release(env)
            env.attr.git.api.repo = git.Repo( env.attr.git.repo.local_dir )
            await Git.Repo.ensure_branch(env)

        @staticmethod
        async def init_all_submodules(env):
            try:
                env = env.branch()
                await env.attr.resources.git.acquire(env)
                await Git.Repo.command(env, "git submodule update --init --recursive")
            finally:
                env.attr.resources.git.release(env)

        @staticmethod
        async def pull(env):
            with Git.AutoStash():
                env.attr.git.api.repo.remote('origin').pull(depth=config.get('git.depth', default=32), r=True, f=True)

        @staticmethod
        async def ensure_branch(env):
            if not env.attr_exists(".git.repo.branch"):
                return

            repo = env.attr.git.api.repo
            branch_info = env.attr.git.repo.branch

            if branch_info["name"] not in repo.heads:
                branch = repo.create_head(branch_info["name"])
            else:
                branch = repo.heads[branch_info["name"]]

            if 'remote' in branch_info:
                remote = repo.remote( branch_info['remote'] )
                branch.set_tracking_branch( remote.refs[branch_info["name"]] )
                branch.set_commit( remote.refs[branch_info["name"]] )

            repo.head.reset( branch, working_tree=True )

            if 'remote' in branch_info:
                if repo.head.commit != remote.refs[branch_info["name"]].commit:
                    raise Exception("repo head mismatch")


        @staticmethod
        async def prepare_info(env, repo_info):
            env.attr.git.repo.url = repo_info['url']
            if 'branch' in repo_info:
                env.attr.git.branch = repo_info['branch']
