
import asyncio

from ..common import *

from .Compilation import *
from .Run import *

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

        if env.has_attr('.opendream.build.params'):
            dotnet.build.params = Shared.Dotnet.Project.default_params(build.params)
        else:
            dotnet.build.params = {}

        dotnet.build.params['configuration'] = 'Debug'

        env.attr.dotnet.solution.path = env.attr.install.dir
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

        env.attr.restore_env = crenv
        env.attr.compiler_env = cbenv
        env.attr.server_env = senv

    @staticmethod
    def build_ready(env):
        if len( Compilation.get_exe_path(env) ) != 1:
            return False
        if len( Run.get_exe_path(env) ) != 1:
            return False
        return True
    
    @staticmethod
    async def managed_build(env, build_metadata):
        env = env.branch()
        await Builder.build(env)
        if env.attr.restore_env.attr.process.instance.returncode != 0:
            raise Exception("restore failed")
        if env.attr.compiler_env.attr.process.instance.returncode != 0:
            raise Exception("build compile failed")
        if env.attr.server_env.attr.process.instance.returncode != 0:
            raise Exception("server compile failed")
        status = await Shared.Git.Repo.status(env)
        build_metadata['last_build_commit'] = status['branch.oid']