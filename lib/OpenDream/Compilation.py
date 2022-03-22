
import Shared

class Compilation(object):
    @staticmethod
    def convert_args(args):
        s = ""
        if "flags" in args:
            for flag in args["flags"]:
                s += f"--{flag} "
        return s

    @staticmethod
    def get_exe_path(env):
        return f"{env.attr.opendream.install.dir}/DMCompiler"

    @staticmethod
    async def compile(env):
        async def log_returncode(env):
            with open(env.attr.opendream.compilation.dm_file.parent / 'compile.returncode.log', "w") as f:
                f.write( str(env.attr.process.p.returncode) )

        compilation = env.attr.opendream.compilation
        if not env.attr_exists('.opendream.compilation.args'):
            compilation.args = {}

        env = env.branch()
        env.attr.shell.dir = env.attr.opendream.compilation.dm_file.parent
        env.attr.process.log_mode = None
        env.attr.process.log_path = env.attr.opendream.compilation.dm_file.parent / 'compile.log.txt'
        env.attr.shell.command = f"{Compilation.get_exe_path(env)} {Compilation.convert_args(compilation.args)} {compilation.dm_file}"
        env.event_handlers['process.complete'] = log_returncode
        await Shared.Process.shell(env)