
import asyncio, shutil, os

import Shared

class Source(object):
    @staticmethod
    def load(env, _id):
        source = env.prefix('.clopendream.source')
        source.id = _id
        source.platform = 'clopendream'
        source.dir = env.attr.clopendream.dirs.sources / source.id

class Builder(object):
    @staticmethod
    def prepare_commandline(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / 'ClopenDreamCommandLine' / 'ClopenDreamCommandLine.csproj'

    @staticmethod
    async def build(env):
        source = env.prefix('.clopendream.source')
        env.attr.dotnet.solution.path = source.dir

        if env.attr_exists('.clopendream.build.params'):
            env.attr.dotnet.build.params = Shared.Dotnet.Project.default_params(env.attr.clopendream.build.params)
        else:
            env.attr.dotnet.build.params = {}

        if 'configuration' not in env.attr.dotnet.build.params:
            env.attr.dotnet.build.params['configuration'] = "Debug"

        env2 = env.branch()
        Builder.prepare_commandline( env2 )
        env3 = env2.branch()
        await Shared.Dotnet.Project.restore( env3 )
        env3 = env2.branch()
        await Shared.Dotnet.Project.build( env3 )


    