
import asyncio

import os
import pathlib

import Shared

class Source(object):
    @staticmethod
    def load(env, _id):
        source = env.prefix('.opendream.source')
        source.id = _id
        source.platform = 'opendream'
        source.dir = env.attr.opendream.dirs.sources / source.id

class Install(object):
    @staticmethod
    def load(env, _id):
        install = env.prefix('.opendream.install')
        install.id = _id
        install.platform = 'opendream'
        install.dir = env.attr.opendream.dirs.installs / install.id

        env.attr.install = install

class Builder(object):
    @staticmethod
    def prepare_compiler_project(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / "DMCompiler" / 'DMCompiler.csproj'

    @staticmethod
    def prepare_server_project(env):
        env.attr.dotnet.project.path = env.attr.dotnet.solution.path / 'OpenDreamServer' / 'OpenDreamServer.csproj'

    @staticmethod
    @Shared.wf_tag('opendream.build')
    async def build(env):
        source = env.prefix('.opendream.source')
        build = env.prefix('.opendream.build')
        dotnet = env.prefix('.dotnet')

        dotnet.solution.path = source.dir

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
        elif build.mode == "build":
            await Shared.Dotnet.Project.build( env2 )

        env2 = env.branch()
        Builder.prepare_server_project( env2 )

        if build.mode == "publish":
            await Shared.Dotnet.Project.publish( env2 )
        elif build.mode == "build":
            await Shared.Dotnet.Project.build( env2 )
