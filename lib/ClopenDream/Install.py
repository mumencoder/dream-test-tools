
import os 
import json

import Shared, Byond

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
    def write_config(env):
        d = os.path.join( os.path.dirname( Install.get_exe_path(env) ), 'config.json' )
        with open(d, "w") as f:
            json.dump(env.attr.clopendream.config, f, cls=Shared.Json.BetterEncoder)

    @staticmethod
    def copy_stdlib(env):
        dmstandard_from_path = source.dir / 'OpenDream' / 'DMCompiler' / 'DMStandard'
        dmstandard_to_path = source.dir / 'ClopenDreamCommandLine' / 'bin'
        dmstandard_to_path = dmstandard_to_path / env.attr.dotnet.build.params['configuration'] / 'net6.0' / "DMStandard"
        if os.path.exists(dmstandard_to_path):
            shutil.rmtree(dmstandard_to_path)
        shutil.copytree(dmstandard_from_path, dmstandard_to_path)
                
    @staticmethod
    async def parse(env):
        env = env.branch()
        command = f"{Install.get_exe_path(env)[0]} parse "
        command += f"{env.attr.byond.codetree} "
        command += f"--working_dir {env.attr.clopendream.install.working_dir} "
        env.attr.shell.command = command
        await Shared.Process.shell(env)

    @staticmethod
    async def compare(clenv, oenv):
        env = clenv.branch()
        command = f"{Install.get_exe_path(env)[0]} compare "
        command += f"{clenv.attr.clopendream.ast1} "
        command += f"{clenv.attr.clopendream.ast2} "
        command += f"--working_dir {env.attr.clopendream.install.working_dir} "
        env.attr.shell.command = command
        await Shared.Process.shell(env)