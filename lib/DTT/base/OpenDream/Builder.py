
import asyncio

import os
import pathlib

import Shared

class Builder(object):
    @staticmethod
    def prepare_compiler_project(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / "DMCompiler" / 'DMCompiler.csproj'

    @staticmethod
    def prepare_server_project(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / 'OpenDreamServer' / 'OpenDreamServer.csproj'

    @staticmethod
    @Shared.Workflow.Decorators.status('opendream.build')
    async def build(env):
        build = env.prefix('.opendream.build')
        dotnet = env.prefix('.dotnet')

        if env.attr_exists('.opendream.build.params'):
            dotnet.build.params = Shared.Dotnet.Project.default_params(build.params)
        else:
            dotnet.build.params = {}

        env2 = env.branch()
        Builder.prepare_compiler_project( env2 )

        env3 = env2.branch()
        await Shared.Dotnet.Project.restore( env3 )
        env3 = env2.branch()
        if build.mode == "publish":
            await Shared.Dotnet.Project.publish( env2 )
        else:
            await Shared.Dotnet.Project.build( env2 )

        env2 = env.branch()
        Builder.prepare_server_project( env2 )

        if build.mode == "publish":
            await Shared.Dotnet.Project.publish( env2 )
        else:
            await Shared.Dotnet.Project.build( env2 )
