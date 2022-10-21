
import asyncio

import os
import pathlib

from .Compilation import *
from .Run import *
import Shared

class Builder(object):
    @staticmethod
    def prepare_compiler_project(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / "DMCompiler" / 'DMCompiler.csproj'

    @staticmethod
    def prepare_server_project(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / 'OpenDreamServer' / 'OpenDreamServer.csproj'

    @staticmethod
    async def build(env):
        build = env.prefix('.opendream.build')
        dotnet = env.prefix('.dotnet')

        if env.attr_exists('.opendream.build.params'):
            dotnet.build.params = Shared.Dotnet.Project.default_params(build.params)
        else:
            dotnet.build.params = {}

        dotnet.build.params['configuration'] = 'Release'

        cenv = env.branch()
        Builder.prepare_compiler_project( cenv )

        crenv = cenv.branch()
        await Shared.Dotnet.Project.restore( crenv )

        cbenv = cenv.branch()
        if build.mode == "publish":
            await Shared.Dotnet.Project.publish( cbenv )
        else:
            await Shared.Dotnet.Project.build( cbenv )

        senv = env.branch()
        Builder.prepare_server_project( senv )

        if build.mode == "publish":
            await Shared.Dotnet.Project.publish( senv )
        else:
            await Shared.Dotnet.Project.build( senv )

    @staticmethod
    def build_ready(env):
        if len( Compilation.get_exe_path(env) ) != 1:
            return False
        if len( Run.get_exe_path(env) ) != 1:
            return False
        return True