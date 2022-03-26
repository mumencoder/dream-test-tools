
import os
import shutil
import json

import Shared

class Install(object):
    @staticmethod
    def load(env, _id):
        install = env.prefix('.clopendream.install')
        install.id = _id
        install.platform = 'clopendream'
        install.dir = env.attr.clopendream.dirs.installs / install.id

        env.attr.install = install

    @staticmethod
    def get_exe_path(env):
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.clopendream.install.dir):
            for filename in files:
                if filename == "ClopenDreamCommandLine":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod
    def copy_stdlib(env):
        exe_path = Install.get_exe_path(env)[0]
        install = env.attr.clopendream.install
        dmstandard_from_path = install.dir / 'OpenDream' / 'DMCompiler' / 'DMStandard'
        dmstandard_to_path = os.path.join(os.path.dirname(exe_path), 'DMStandard')
        if os.path.exists(dmstandard_to_path):
            shutil.rmtree(dmstandard_to_path)
        shutil.copytree(dmstandard_from_path, dmstandard_to_path)

    @staticmethod
    async def parse(env):
        config = {}
        config["byond_codetree_path"] = env.attr.byond.codetree
        config["ast_path"] = env.attr.clopendream.install.working_dir / 'clopen_ast.json'
        config["empty_dir"] = env.attr.dirs.state / 'empty'
        input_path = env.attr.clopendream.install.working_dir / 'parse_input.json'
        output_path = env.attr.clopendream.install.working_dir / 'parse_output.json'
        with open(input_path, "w") as f:
            json.dump(config, f, cls=Shared.Json.BetterEncoder)

        env = env.branch()
        command = f"{Install.get_exe_path(env)[0]} parse "
        command += f"{input_path} "
        command += f"{output_path} "
        env.attr.shell.command = command
        await Shared.Process.shell(env)

    @staticmethod
    async def compare(env):
        config = {}
        config["ast_1"] = env.attr.clopendream.run.ast1
        config["ast_2"] = env.attr.clopendream.run.ast2
        config["mismatch_dir"] = env.attr.clopendream.run.working_dir / 'mismatch'
        input_path = env.attr.clopendream.run.working_dir / 'compare_input.json'
        output_path = env.attr.clopendream.run.working_dir / 'compare_output.json'
        with open(input_path, "w") as f:
            json.dump(config, f, cls=Shared.Json.BetterEncoder)

        env = env.branch()
        command = f"{Install.get_exe_path(env)[0]} compare "
        command += f"{input_path} "
        command += f"{output_path} "
        env.attr.shell.command = command
        await Shared.Process.shell(env)