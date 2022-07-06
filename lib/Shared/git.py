import os, subprocess
import collections
import asyncio
import git

import Shared

class Git(object):
    class AutoStash(object):
        async def __enter__(self):
            await Git.Repo.command(env, "git stash push -u")

        async def __exit__(self, exc_type, exc_value, exc_traceback):
            await Git.Repo.command(env, "git stash pop")

    @staticmethod
    def nightly_builds(commits):
        nights = collections.defaultdict(list)
        for commit in commits:
            h = tuple( [getattr(commit.committed_datetime, attr) for attr in ["year", "month", "day"]] )
            nights[h].append( commit )
        return [max(commits, key=lambda c: c.committed_date) for commits in nights.values()]

    @staticmethod
    def weekly_builds(commits):
        weeks = collections.defaultdict(list)
        for commit in commits:
            h = tuple( [getattr(commit.committed_datetime, attr) for attr in ["year", "month", "day"]] )
            week = h[0] * 60 + h[1] * 5 + int(h[2] / 7)
            weeks[week].append( commit )
        return [max(commits, key=lambda c: c.committed_date) for commits in weeks.values()]

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
                if len(q) == 0:
                    return
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
        async def init_all_submodules(env):
            res = await env.attr.resources.git.acquire()
            try:
                env = env.branch()
                cmd = "git submodule update --init --recursive "
                if env.attr_exists(".git.repo.submodule_ref"):
                    cmd += f"--reference {env.attr.git.repo.submodule_ref} "
                await Git.Repo.command(env, cmd)
            finally:
                env.attr.resources.git.release(res)

        def search_base_commit(env, start, potential_matches, max_level=32):
            repo = env.attr.git.api.repo
            current_commits = [ repo.commit(start) ]

            while max_level > 0:
                max_level -= 1
                new_current_commits = []
                for commit in current_commits:
                    if str(commit) in potential_matches:
                        return commit
                    new_current_commits += commit.parents
                current_commits = new_current_commits

            return None

        async def resolve_head(env):
            repo = env.attr.git.api.repo
            env.attr.git.ref = repo.heads[ env.attr.git.branch.name ]

        async def ensure_branch(env):
            branch_info = env.attr.git.repo.branch
            git = env.prefix('.git')

            if git.branch.name not in repo.heads:
                repo.create_head( git.branch.name )

            Git.Repo.resolve_head(env)

            if env.attr_exists('.git.repo.remote'):
                remote = repo.remote( git.remote.name )
                if git.branch.name not in remote.refs:
                    remote.fetch( git.branch.name )
                branch.set_tracking_branch( remote.refs[git.branch.name] )
                branch.set_commit( remote.refs[git.branch.name] )

            repo.head.reset( git.branch.name, working_tree=True )

            if env.attr_exists('.git.repo.remote'):
                if repo.head.commit != remote.refs[git.branch.name].commit:
                    raise Exception("repo head mismatch")

        @staticmethod
        async def ref(env, ref, remote=None):
            repo = env.attr.git.api.repo
            if remote is None:
                return repo.refs[ref]
            else:
                return repo.remote(remote).refs[ref]

        @staticmethod
        async def ensure_commit(env):
            repo = env.attr.git.api.repo
            if env.attr_exists('.git.repo.remote') and env.attr.git.repo.commit not in env.attr.git.api.repo.refs:
                print("fetch", env.attr.git.repo.commit)
                repo.remote(env.attr.git.repo.remote).fetch( env.attr.git.repo.commit )
            repo.head.reset( env.attr.git.repo.commit, working_tree=True )

        @staticmethod
        async def freshen(env):
            repo = env.attr.git.api.repo
            repo.head.reset( 'origin/HEAD', working_tree=True )
            repo.remote('origin').pull()

        @staticmethod
        def load(env):
            env.attr.git.api.repo = git.Repo( env.attr.git.repo.local_dir )

        @staticmethod
        async def ensure(env):
            if not Git.Repo.exists(env):
                with Shared.Workflow.status(env, "waiting git"):
                    res = await env.attr.resources.git.acquire()
                    try:
                        cmd = "git clone "
                        if env.attr_exists('.git.repo.clone_depth'):
                            cmd += f"--depth {env.attr.git.repo.clone_depth} "
                        if env.attr_exists('.git.repo.branch'):
                            cmd += f"--branch {env.attr.git.repo.branch['name']} "
                        if not env.attr_exists('.git.repo.url'):
                            raise Exception("URL not set for ensure")
                        cmd += f"{env.attr.git.repo.url} {env.attr.git.repo.local_dir} "
                        env.attr.shell.command = cmd
                        env.attr.wf.status[-1] = "git clone"
                        await Shared.Process.shell(env)
                    finally:
                        env.attr.resources.git.release(res)
            Git.Repo.load(env)
