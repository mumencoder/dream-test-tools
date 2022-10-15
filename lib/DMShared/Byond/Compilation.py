
import os
import Shared

class Compilation(object):
    @staticmethod
    def convert_args(args={}):
        preargs = ""
        postargs = ""
        if "code_tree" in args:
            preargs += "-code_tree "
        if "obj_tree" in args:
            preargs += "-o "
        return (preargs, postargs)

    @staticmethod
    async def compile(env):
        async def log_returncode(env):
            env.attr.compilation.returncode = env.attr.process.p.returncode

        env = env.branch()
        if not env.attr_exists('.compilation.args'):
            env.attr.compilation.args = {}

        proc_env = os.environ
        proc_env.update( {'LD_LIBRARY_PATH':f"{env.attr.install.dir}/byond/bin"} )
        env.attr.shell.env = proc_env
        preargs, postargs = Compilation.convert_args(env.attr.compilation.args)
        env.attr.shell.command = f"{env.attr.install.dir}/byond/bin/DreamMaker {preargs} {env.attr.compilation.dm_file_path} {postargs}"
        env.event_handlers['process.finished'] = log_returncode
        await Shared.Process.shell(env)

    @staticmethod
    async def generate_code_tree(env):
        if env.attr.compilation.flags.recompile is False and os.path.exists(env.attr.compilation.out):
            return
        env.attr.compilation.args = {'code_tree':True}
        env.attr.process.log_mode = None
        env.attr.process.log_path = env.attr.compilation.out
        await Compilation.compile(env)

    @staticmethod
    async def generate_obj_tree(env):
        if env.attr.compilation.flags.recompile is False and os.path.exists(env.attr.compilation.out):
            return
        env.attr.compilation.args = {'obj_tree':True}
        await Compilation.compile(env)