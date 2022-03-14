
import os 
import json

import Shared, Byond

class Install(object):
    @staticmethod
    def get_exe_path(env):
        return f"{env.attr.clopendream.install.dir}/ClopenDreamCommandLine/bin/Debug/net6.0/ClopenDreamCommandLine"

    @staticmethod
    def write_config(env):
        d = os.path.join( os.path.dirname( Install.get_exe_path(env) ), 'config.json' )
        with open(d, "w") as f:
            json.dump(env.attr.clopendream.config, f, cls=Shared.Json.BetterEncoder)

    @staticmethod
    async def parse(env):
        env = env.branch()
        command = f"{Install.get_exe_path(env)} parse "
        command += f"{env.attr.byond.codetree} "
        command += f"--working_dir {env.attr.clopendream.install.working_dir} "
        env.attr.shell.command = command
        await Shared.Process.shell(env)

    @staticmethod
    async def compare(clenv, oenv):
        env = clenv.branch()
        command = f"{Install.get_exe_path(env)} compare "
        command += f"{clenv.attr.clopendream.ast1} "
        command += f"{clenv.attr.clopendream.ast2} "
        command += f"--working_dir {env.attr.clopendream.install.working_dir} "
        env.attr.shell.command = command
        await Shared.Process.shell(env)