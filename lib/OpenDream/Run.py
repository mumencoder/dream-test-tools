
import Shared

class Run(object):
    @staticmethod
    def convert_args(args):
        return ""

    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.json')

    @staticmethod
    def get_exe_path(env):
        return f"{env.attr.opendream.install.dir}/OpenDreamServer"

    @staticmethod 
    async def run(env):
        run = env.attr.opendream.run
        env = env.branch()
        try:
            await env.attr.resources.opendream_server.acquire(env)
            env.attr.shell.command = f"{Run.get_exe_path(env)} {Run.convert_args(run.args)} --cvar opendream.json_path={run.file}"
            env.attr.shell.dir = env.attr.opendream.install.dir
            await Shared.Process.shell(env)
        finally:
            env.attr.resources.opendream_server.release(env)
