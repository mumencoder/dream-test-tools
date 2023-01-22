
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
    async def invoke_compiler(env):
        penv = env.branch()
        if not penv.attr_exists('.compilation.args'):
            penv.attr.compilation.args = []

        proc_env = os.environ
        proc_env.update( {'LD_LIBRARY_PATH':f"{penv.attr.install.dir}/byond/bin"} )
        penv.attr.shell.env = proc_env
        penv.attr.shell.command = Compilation.create_dreammaker_command( penv, penv.attr.compilation.args )
        await Shared.Process.shell(penv)
        env.attr.compilation.returncode = penv.attr.process.instance.returncode

    async def managed_compile(env):
        env = env.branch()
        env.attr.process.stdout = open(env.attr.compilation.root_dir / 'byond.compile.stdout.txt', "w")
        try:
            await Compilation.invoke_compiler(env)
        finally:
            env.attr.process.stdout.close()

        with open(env.attr.compilation.root_dir / 'byond.compile.returncode.txt', "w") as f:
            f.write( str(env.attr.compilation.returncode) )

        return env

    def load_compile(env):
        with open( env.attr.compilation.root_dir / 'byond.compile.stdout.txt', "r" ) as f:
            env.attr.compilation.stdout = f.read()
        with open( env.attr.compilation.root_dir / 'byond.compile.returncode.txt', "r" ) as f:
            env.attr.compilation.returncode = int(f.read())

    async def managed_codetree(env):
        env = env.branch()
        env.attr.compilation.args = ["code_tree"]
        env.attr.process.stdout = open(env.attr.compilation.root_dir / 'byond.compile.stdout.txt', "w")
        try:
            await Compilation.invoke_compiler(env)
        finally:
            env.attr.process.stdout.close()

        with open(env.attr.metadata.get_path("byond.codetree.returncode"), "w") as f:
            f.write( str(env.attr.compilation.returncode) )

        return env