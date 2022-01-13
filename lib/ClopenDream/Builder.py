
import asyncio, shutil, os

import Shared

class Builder(object):
    @staticmethod
    def prepare_commandline(config):
        config['dotnet.project.path'] = config['dotnet.solution.path'] / 'ClopenDreamCommandLine' / 'ClopenDreamCommandLine.csproj'

    @staticmethod
    async def build(config):
        config["dotnet.solution.path"] = config["clopendream.install.dir"]

        config = config.branch('build_clopen')
        if not config.exists('dotnet.project.params'):
            config['dotnet.project.params'] = {}
        config['dotnet.project.params'] = Shared.Dotnet.Project.default_params(config['dotnet.project.params'])

        Builder.prepare_commandline( config )
        process = await Shared.Dotnet.Project.build( config )
        await asyncio.wait_for(process.wait(), timeout=None)

        dmstandard_from_path = config["clopendream.install.dir"] / 'OpenDream' / 'DMCompiler' / 'DMStandard'
        dmstandard_to_path = config["clopendream.install.dir"] / 'ClopenDreamCommandLine' / 'bin'
        dmstandard_to_path = dmstandard_to_path / config["dotnet.project.params"]['configuration'] / 'net6.0' / "DMStandard"
        shutil.rmtree(dmstandard_to_path)
        shutil.copytree(dmstandard_from_path, dmstandard_to_path)
    