
import os 

import Shared, Byond

class Install(object):
    @staticmethod
    def set_current(config, _id):
        config['clopendream.install.id'] = _id
        config["clopendream.install.dir"] = config['clopendream.dirs.builds'] / config['clopendream.install.id']

    @staticmethod
    def command_line(config):
        return f"{config['clopendream.install.dir']}/ClopenDreamCommandLine/bin/Debug/net6.0/ClopenDreamCommandLine"

    @staticmethod
    async def test_parse(config):
        config = config.branch('test_parse')
        command = Install.command_line(config)
        command += f" test-parse {config['byond.codetree.out']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        process = await Shared.Process.shell(config, command)
        return process

    @staticmethod
    async def compare(config):
        config = config.branch('compare')
        command = Install.command_line(config)
        command += f" compare {config['byond.codetree.out']} {config['clopendream.input_dm']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        process = await Shared.Process.shell(config, command)
        return process

    @staticmethod
    async def object_hash(config):
        config = config.branch('object-hash')
        command = Install.command_line(config)
        command += f" object-hash {config['byond.codetree.out']} {config['clopendream.input_dm']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        process = await Shared.Process.shell(config, command)
        return process

    @staticmethod
    async def compile(config):
        config = config.branch('compile')
        command = Install.command_line(config)
        command += f" compile {config['byond.codetree.out']}"
        command += f" --working_dir {config['clopendream.output.base_dir']}"
        process = await Shared.Process.shell(config, command)
        return process
