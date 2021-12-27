
import asyncio
import Shared

class Install(object):
    @staticmethod
    def set_current(config, _id):
        config['opendream.build.id'] = _id
        config["opendream.install_dir"] = config['opendream.dirs.builds'] / config['opendream.build.id']

    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.json')

    @staticmethod
    async def compile(config, file, args=""):
        command = f"{config['opendream.install_dir']}/DMCompiler/bin/Debug/net6.0/DMCompiler {args} {file}"
        process = await Shared.Process.shell(config, command)
        return process
            
    @staticmethod 
    async def run(config, file, args=""):
        command = f"{config['opendream.install_dir']}/bin/Content.Server/OpenDreamServer {args} --cvar opendream.json_path={file}"
        process = await Shared.Process.shell(config, command)
        return process
