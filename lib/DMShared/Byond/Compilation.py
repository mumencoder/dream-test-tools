
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
        async def log_returncode(eenv):
            env.attr.compilation.returncode = eenv.attr.process.instance.returncode

        penv = env.branch()
        if not penv.attr_exists('.compilation.args'):
            penv.attr.compilation.args = {}

        proc_env = os.environ
        proc_env.update( {'LD_LIBRARY_PATH':f"{penv.attr.install.dir}/byond/bin"} )
        penv.attr.shell.env = proc_env
        preargs, postargs = Compilation.convert_args(penv.attr.compilation.args)
        penv.attr.shell.command = f"{penv.attr.install.dir}/byond/bin/DreamMaker {preargs} {penv.attr.compilation.dm_file_path} {postargs}"
        penv.event_handlers['process.finished'] = log_returncode
        await Shared.Process.shell(penv)

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