
import asyncio

import os
import pathlib

import Shared

class Builder(object):
    @staticmethod
    def prepare_compiler_build(config):
        config['dotnet.project.path'] = config['dotnet.solution.path'] / 'DMCompiler' / 'DMCompiler.csproj'

    @staticmethod
    def prepare_server_build(config):
        config['dotnet.project.path'] = config['dotnet.solution.path'] / 'OpenDreamServer' / 'OpenDreamServer.csproj'

    @staticmethod
    async def build(config):
        config["dotnet.project.params"] = { }

        Builder.prepare_compiler_build( config )
        process = await Shared.Dotnet.Project.restore( config )
        await asyncio.wait_for(process.wait(), timeout=None)

        process = await Shared.Dotnet.Project.build( config )
        await asyncio.wait_for(process.wait(), timeout=None)

        Builder.prepare_server_build( config )
        process = await Shared.Dotnet.Project.build( config )
        await asyncio.wait_for(process.wait(), timeout=None)        