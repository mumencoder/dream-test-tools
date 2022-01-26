import os, subprocess
import collections
import asyncio
import git

import Shared

class Git(object):
    @staticmethod
    def nightly_builds(commits):
        nights = collections.defaultdict(list)
        for commit in commits:
            h = tuple( [getattr(commit.committed_datetime, attr) for attr in ["year", "month", "day"]] )
            nights[h].append( commit )
        return [max(commits, key=lambda c: c.committed_date) for commits in nights.values()]

    class Repo(object):
        @staticmethod 
        def commit_history(config, commit, depth=32):
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
        async def command(config, command):
            with Shared.folder.Push(config['git.local_dir']):
                process = await Shared.Process.shell(config, command)
                await asyncio.wait_for(process.wait(), timeout=None)

        @staticmethod
        def exists(config):
            if not os.path.exists(config['git.local_dir']):
                os.mkdir( config['git.local_dir'] )
            with Shared.folder.Push(config['git.local_dir']):
                process = subprocess.run('git status', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                if process.returncode == 0:
                    return True
                else:
                    return False

        @staticmethod
        def ensure_repo(config, url):
            if not Git.Repo.exists(config):
                subprocess.run(f"git clone --depth 32 --no-single-branch {url} {config['git.local_dir']}", shell=True)
            try:
                config['git.repo'] = git.Repo( config['git.local_dir'] )
            except Exception as e:
                print(e)

        @staticmethod
        def ensure_branch(config, remote_name, branch_name):
            repo = config['git.repo']
            remote = repo.remote( remote_name )
            if branch_name not in repo.refs:
                branch = repo.create_head(branch_name)
                branch.set_tracking_branch( remote.refs[branch_name] )
                branch.set_commit( remote.refs[branch_name] )
            repo.refs[branch_name].checkout()
            repo.head.reset( remote.refs[branch_name], working_tree=True )

        @staticmethod 
        def reset(config, remote_name):
            repo = config['git.repo']
            remote = repo.remote( remote_name )
            repo.head.reset( remote.refs.HEAD, working_tree=True )