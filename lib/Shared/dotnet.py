
import asyncio
import Shared

class Dotnet(object):
    class Project(object):
        build_param_map = {"install_dir": "-o"}
        @staticmethod
        def flatten_build_params(params):
            s = ""
            for k, v in params.items():
                if k not in Dotnet.Project.build_param_map:
                    s += f"--{k} {v} "
                else:
                    s += f"{Dotnet.Project.build_param_map[k]} {v} "
            return s

        @staticmethod
        def default_params(params):
            if 'configuration' not in params:
                params['configuration'] = "Debug"
            return params
            
        @staticmethod
        @Shared.wf_tag('dotnet.restore')
        async def restore(env):
            params = env.get('.dotnet.restore.params', {})
            env.attr.shell.command = f"dotnet restore {env.attr.dotnet.project.path} {Dotnet.Project.flatten_build_params(params)}"
            await Shared.Process.shell(env)
            
        @staticmethod
        @Shared.wf_tag('dotnet.build')
        async def build(env):
            params = env.get('.dotnet.build.params', {})
            env.attr.shell.command = f"dotnet build -clp:ErrorsOnly {env.attr.dotnet.project.path} {Dotnet.Project.flatten_build_params(params)}"
            await Shared.Process.shell(env)

