
import os
import Shared, ClopenDream, OpenDream

class App(object):
    def __init__(self):
        self.load_configs()
        self.test_output_dir = self.config['storage_dir'] / 'tests' 

    def load_configs(self):
        self.config = Shared.Config()
        config_dir = os.path.abspath( os.path.expanduser("~/dream-storage/config") )
        for file_path in os.listdir( config_dir ):
            config_path = os.path.join(config_dir, file_path)
            config_fns = Shared.Object.import_file( config_path )
            if hasattr(config_fns, 'setup' ):
                config_fns.setup( self.config )
            if hasattr(config_fns, 'defaults' ):
                config_fns.defaults( self.config )

    async def prepare_repo(self, url, local_dir, branch=None):
        config = self.config
        config['git.local_dir'] = local_dir
        config["dotnet.solution.path"] = config['git.local_dir']
        Shared.Git.Repo.ensure_repo(config, url)
        await Shared.Git.Repo.command(config, "git stash")
        config['git.repo'].remote('origin').pull(depth=32, r=True, f=True)
        await Shared.Git.Repo.command(config, "git stash pop")
        await Shared.Git.Repo.command(config, "git submodule update --init --recursive")

    async def prepare_ss13_repo(self, repo_info):
        config = self.config
        config['git.local_dir'] = self.config['ss13.base_dir']
        config["dotnet.solution.path"] = config['git.local_dir']
        Shared.Git.Repo.ensure_repo(config, repo_info['url'])
        if 'branch' in repo_info:
            Shared.Git.Repo.ensure_branch(config, 'origin', repo_info['branch'])
            pass
        else:
            Shared.Git.Repo.reset(config, 'origin')
        await Shared.Git.Repo.command(config, "git stash")
        config['git.repo'].remote('origin').pull(depth=1, f=True)
        await Shared.Git.Repo.command(config, "git stash pop")

    async def prepare_clopendream_local(self, _id, local_dir):
        ClopenDream.Install.set_current(self.config, _id)
        Shared.Path.sync_folders( local_dir, self.config['clopendream.install_dir'] )

    async def prepare_clopendream_repo(self, _id):
        ClopenDream.Install.set_current(self.config, _id)
        await self.prepare_repo(self.config['clopendream.repo_url'], self.config['clopendream.install_dir'])

    async def prepare_opendream_local(self, _id, local_dir):
        OpenDream.Install.set_current(self.config, _id)
        Shared.Path.sync_folders( local_dir, self.config['opendream.install_dir'] )

    async def prepare_opendream_repo(self, _id):
        OpenDream.Install.set_current(self.config, _id)
        await self.prepare_repo(self.config['opendream.repo_url'], self.config['opendream.install_dir'])
