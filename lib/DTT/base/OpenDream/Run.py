
import os

import Shared

class Run(object):
    base_port = 25566
    current_port = 0

    @staticmethod
    def get_port():
        Run.current_port = (Run.current_port + 1) % 200
        return Run.current_port + Run.base_port

    @staticmethod
    def convert_args(args):
        return ""

    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.json')

    @staticmethod
    def get_exe_path(env):
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.install.dir):
            for filename in files:
                if filename == "OpenDreamServer":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod 
    async def run(env):
        run = env.attr.run
        env = env.branch()
        exe_paths = Run.get_exe_path(env)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", exe_paths)
        res = await env.attr.resources.opendream_server.acquire()
        try:
            cmd = f"{exe_paths[0]} {Run.convert_args(run.args)} "
            cmd += f"--cvar opendream.json_path={run.dm_file_path} "
            cmd += f"--cvar net.port={Run.get_port()} "
            env.attr.shell.command = cmd
            print( env.attr.shell.command )
            env.attr.shell.dir = env.attr.install.dir
            await Shared.Process.shell(env)
        finally:
            env.attr.resources.opendream_server.release(res)
