
import os 

import Shared, Byond

class Install(object):
    @staticmethod
    def set_current(config, _id):
        config['clopendream.build.id'] = _id
        config["clopendream.install_dir"] = config['clopendream.dirs.builds'] / config['clopendream.build.id']

    @staticmethod
    def command_line(config):
        return f"{config['clopendream.install_dir']}/ClopenDreamCommandLine/bin/Debug/net6.0/ClopenDreamCommandLine"

    @staticmethod
    async def test_parse(config):
        config = config.branch('test_parse')
        command = Install.command_line(config)
        command += f" test-parse {config['byond.codetree.out']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        print(command)
        process = await Shared.Process.shell(config, command)
        return process

    @staticmethod
    async def compare(config):
        config = config.branch('compare')
        command = Install.command_line(config)
        command += f" compare {config['byond.codetree.out']} {config['ss13.dme_file']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        print(command)
        process = await Shared.Process.shell(config, command)
        return process

    @staticmethod
    async def object_hash(config):
        config = config.branch('object-hash')
        command = Install.command_line(config)
        command += f" object-hash {config['byond.codetree.out']} {config['ss13.dme_file']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        print(command)
        process = await Shared.Process.shell(config, command)
        return process

    @staticmethod
    async def compile(config):
        config = config.branch('compile')
        command = Install.command_line(config)
        command += f" compile {config['byond.codetree.out']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        print(command)
        process = await Shared.Process.shell(config, command)
        return process
