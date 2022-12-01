
from ..common import *

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
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.build.dir):
            for filename in files:
                if filename == "DMCompiler":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod
    async def compile(env):
        compilation = env.attr.compilation

        async def log_returncode(env):
            compilation.returncode = env.attr.process.instance.returncode

        if not env.attr_exists('.compilation.args'):
            compilation.args = {}

        await env.send_event('opendream.before_compile', env)

        env = env.branch()
        env.attr.shell.dir = compilation.dm_file_path.parent

        exe_paths = Compilation.get_exe_path(env)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", env.attr.build.dir, exe_paths)

        env.attr.shell.command = f"{exe_paths[0]} {Compilation.convert_args(compilation.args)} {compilation.dm_file_path.name}"
        env.attr.shell.env = {}
        env.event_handlers['process.finished'] = log_returncode
        await Shared.Process.shell(env)