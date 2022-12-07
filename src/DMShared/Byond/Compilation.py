
from ..common import *

class Compilation(object):
    @staticmethod
    def create_dreammaker_command(penv, args=[]):
        preargs = ""
        postargs = ""
        for arg in args:
            if arg == "code_tree":
                preargs += "-code_tree "
            if arg == "obj_tree":
                preargs += "-o "
        return f"{penv.attr.install.dir}/byond/bin/DreamMaker {preargs} {penv.attr.compilation.dm_file_path} {postargs}"

    @staticmethod
    async def compile(env):
        async def log_returncode(eenv):
            env.attr.compilation.returncode = eenv.attr.process.instance.returncode

        penv = env.branch()
        if not penv.attr_exists('.compilation.args'):
            penv.attr.compilation.args = []

        proc_env = os.environ
        proc_env.update( {'LD_LIBRARY_PATH':f"{penv.attr.install.dir}/byond/bin"} )
        penv.attr.shell.env = proc_env
        penv.attr.shell.command = Compilation.create_dreammaker_command( penv, penv.attr.compilation.args )
        penv.event_handlers['process.finished'] = log_returncode
        await Shared.Process.shell(penv)