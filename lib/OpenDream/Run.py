
import os

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
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.opendream.install.dir):
            for filename in files:
                if filename == "OpenDreamServer":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod 
    async def run(env):
        run = env.attr.opendream.run
        env = env.branch()
        exe_paths = Run.get_exe_path(env)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", exe_paths)
        try:
            await env.attr.resources.opendream_server.acquire(env)
            env.attr.shell.command = f"{exe_paths[0]} {Run.convert_args(run.args)} --cvar opendream.json_path={run.file}"
            env.attr.shell.dir = env.attr.opendream.install.dir
            await Shared.Process.shell(env)
        finally:
            env.attr.resources.opendream_server.release(env)
