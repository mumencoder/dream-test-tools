
from .common import *

class Git(object):
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
        env.attr.shared_repo.source = Git.RepoSource(env, 
            env.attr.shared_repo.root_dir, 
            env.attr.shared_repo.name,
            limit=env.attr.shared_repo.limit)
        for i in range(0, env.attr.shared_repo.limit):
            res = env.attr.shared_repo.source.get_resource_data(i)
            await Shared.Path.full_sync_folders(env, env.attr.git.repo.local_dir, res['path'])
        env.attr.task.export( env, ".shared_repo.source" )

    def acquire_shared_repo(env):
        while True:
            repo = await senv.attr.shared_repo.source.acquire()
            if repo is not None:
                break
            await asyncio.sleep(0.1)
        senv.attr.shared_repo.resource = repo
        env.attr.task.guard_resource( senv.attr.shared_repo.source, repo )
        senv.attr.git.repo.local_dir = repo["data"]["path"]
        senv.attr.git.remote = 'origin'
        await Shared.Git.Repo.ensure(senv)

    def release_shared_repo(env):
        env.attr.shared_repo.source.release( env.attr.shared_repo.resource)
        env.attr.task.unguard_resource( env.attr.shared_repo.resource )
