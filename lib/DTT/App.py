
import os
import Shared, Byond, ClopenDream, OpenDream

class App(object):
    def __init__(self):
        self.load_configs()

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

    async def install(self, platform, install_id):
        if platform == "byond":
            await self.install_byond(self.config, install_id, self.config['byond.installs'][install_id])
        elif platform == "opendream":
            await self.install_opendream( self.config, install_id, self.config['opendream.installs'][install_id] )
        elif platform == "clopendream":
            await self.install_clopendream( self.config, install_id, self.config['clopendream.installs'][install_id] )
        else:
            raise Exception("unknown install")

    async def install_byond(self, config, install_id, install_info):
        Byond.Install.set_current(config, install_id)
        if install_info["type"] == "web_official":
            Byond.Install.download(config, install_info['version'])
        else:
            raise Exception("unknown install type")

    async def install_opendream(self, config, install_id, install_info):
        OpenDream.Install.set_current(config, install_id)
        if install_info["type"] == "filesystem":
            Shared.Path.sync_folders( install_info["location"], config['opendream.install.dir'] )
            config["dotnet.solution.path"] = config['opendream.install.dir']
        if install_info["type"] == "repo":
            config['git.repo.url'] = install_info["url"]
            config['git.branch'] = install_info["branch"]
            await self.prepare_repo(config, config['opendream.install.dir'])
        config['opendream.build.params'] = {'configuration':'Release'}
        await OpenDream.Builder.build(config)

    async def install_clopendream(self, config, install_id, install_info):
        ClopenDream.Install.set_current(config, install_id)
        if install_info["type"] == "filesystem":
            Shared.Path.sync_folders( install_info["location"], config['clopendream.install.dir'] )
        if install_info["type"] == "repo":
            config['git.repo.url'] = install_info["url"]
            config['git.branch'] = install_info["branch"]
            await self.prepare_repo(config, config['clopendream.install.dir'])
        config['clopendream.build.params'] = {'configuration':'Release'}
        await ClopenDream.Builder.build(config)

    async def prepare_repo(self, config, local_dir):
        config['git.local_dir'] = local_dir
        config["dotnet.solution.path"] = config['git.local_dir']
        Shared.Git.Repo.ensure_repo(config, config['git.repo.url'])
        if config.exists('git.branch'):
            Shared.Git.Repo.ensure_branch(config, 'origin', config['git.branch'])
        else:
            Shared.Git.Repo.reset(config, 'origin')

        await Shared.Git.Repo.command(config, "git stash")
        config['git.repo'].remote('origin').pull(depth=config.get('git.depth', default=32), r=True, f=True)
        await Shared.Git.Repo.command(config, "git stash pop")
        await Shared.Git.Repo.command(config, "git submodule update --init --recursive")

    async def prepare_ss13_repo(self, config, repo_info):
        config['git.repo.url'] = repo_info['url']
        self.prepare_repo( self.config['ss13.base_dir'] )