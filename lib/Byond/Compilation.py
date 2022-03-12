
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
            with open(env.attr.byond.compilation.file_path.parent / 'compile.returncode.log', "w") as f:
                f.write( str(env.attr.process.p.returncode) )

        compilation = env.attr.byond.compilation
        install = env.attr.byond.install

        env = env.branch()
        env.attr.process.env = {'LD_LIBRARY_PATH':f"{install.dir}/byond/bin"}
        preargs, postargs = Compilation.convert_args(compilation.args)
        env.attr.shell.command = f"{install.dir}/byond/bin/DreamMaker {preargs} {compilation.file_path} {postargs}"
        env.event_handlers['process.complete'] = log_returncode
        await Shared.Process.shell(env)

    @staticmethod
    async def generate_code_tree(env):
        compilation = env.attr.byond.compilation
        if compilation.flags.recompile is False and os.path.exists(compilation.out):
            return
        compilation.args = {'code_tree':True}
        env.attr.process.log_mode = None
        env.attr.process.log_path = compilation.out
        await Compilation.compile(env)

    @staticmethod
    async def generate_obj_tree(env):
        compilation = env.attr.byond.compilation
        if compilation.flags.recompile is False and os.path.exists(compilation.out):
            return
        compilation.args = {'obj_tree':True}
        await Compilation.compile(env)