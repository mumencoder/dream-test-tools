
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
        def default_params(config, params):
            if 'configuration' not in params:
                params['configuration'] = "Debug"
            return params
            
        @staticmethod
        async def build(config):
            params = config['dotnet.project.params']
            command = f"dotnet build -clp:ErrorsOnly {config['dotnet.project.path']} {Dotnet.Project.flatten_build_params(params)}"
            print(command)
            process = await Shared.Process.shell(config, command)
            return process

        @staticmethod
        async def restore(config):
            params = config['dotnet.project.params']
            command = f"dotnet restore {config['dotnet.project.path']} {Dotnet.Project.flatten_build_params(params)}"
            print(command)
            process = await Shared.Process.shell(config, command)
            return process