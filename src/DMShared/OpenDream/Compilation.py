
from ..common import *

class Compilation(object):
    @staticmethod
    def convert_args(args):
        s = ""
        for arg in args:
            if type(arg) is dict and arg["type"] == "flags":
                for flag in arg["flags"]:
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
    async def invoke_compiler(env):
        penv = env.branch()
        if not penv.attr_exists('.compilation.args'):
            penv.attr.compilation.args = []

        penv.attr.build.dir = penv.attr.install.dir / 'DMCompiler'
        penv.attr.shell.dir = penv.attr.compilation.dm_file_path.parent
        exe_paths = Compilation.get_exe_path(penv)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", env.attr.build.dir, exe_paths)

        penv.attr.shell.env = os.environ
        penv.attr.shell.command = f"{exe_paths[0]} {Compilation.convert_args(penv.attr.compilation.args)} {penv.attr.compilation.dm_file_path.name}"
        await Shared.Process.shell(penv)
        env.attr.compilation.returncode = penv.attr.process.instance.returncode

    async def managed_compile(env):
        env = env.branch()
        env.attr.process.stdout = open(env.attr.compilation.root_dir / 'opendream.compile.stdout.txt', "w")
        try:
            await Compilation.invoke_compiler(env)
        finally:
            env.attr.process.stdout.close()

        with open(env.attr.compilation.root_dir / 'opendream.compile.returncode.txt', "w") as f:
            f.write( str(env.attr.compilation.returncode) )

        return env

    def load_compile(senv, denv):
        with open( senv.attr.compilation.root_dir / 'opendream.compile.stdout.txt', "r" ) as f:
            denv.attr.compilation.stdout = f.read()
        with open( senv.attr.compilation.root_dir / 'opendream.compile.returncode.txt', "r" ) as f:
            denv.attr.compilation.returncode = int(f.read())

    async def opendream_ast(tenv):
        env = tenv.branch()
        env.attr.compilation.dm_file_path = env.attr.test.root_dir / env.attr.test.metadata.paths.dm_file

        l = List[System.String]()
        l.Add( str(env.attr.compilation.dm_file_path) )
        try:
            tenv.attr.test.open_compile = DMCompiler.DMCompiler.GetAST( l )
        except Exception as e:
            tenv.attr.test.metadata.paths.opendream_throw = 'opendream_throw.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_throw, "w") as f:
                f.write(str(e))

        #DMAST.DMASTNodePrinter().Print(tenv.attr.test.open_compile.ast, System.Console.Out)
        errors = DMCompiler.DMCompiler.errors
        if errors.Count > 0:
            tenv.attr.test.metadata.paths.opendream_errors = 'opendream_errors.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_errors, "w") as f:
                for error in tenv.attr.test.open_compile.parserErrors:
                    f.write( error.ToString() + '\n')
                for error in errors:
                    f.write( error.ToString() + '\n')
        else:
            if tenv.attr_exists( '.test.metadata.paths.opendream_errors' ):
                del tenv.attr.test.metadata.paths.opendream_errors

        warnings = DMCompiler.DMCompiler.warnings
        if warnings.Count > 0:
            tenv.attr.test.metadata.paths.opendream_warnings = 'opendream_warnings.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_warnings, "w") as f:
                for warning in warnings:
                    f.write( warning.ToString() + '\n')
        else:
            if tenv.attr_exists( '.test.metadata.paths.opendream_warnings' ):
                del tenv.attr.test.metadata.paths.opendream_warnings

        Metadata.save_test(tenv)