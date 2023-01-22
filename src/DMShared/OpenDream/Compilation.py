
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
    async def compile(env):
        compilation = env.attr.compilation

        async def log_returncode(env):
            compilation.returncode = env.attr.process.instance.returncode

        if not env.attr_exists('.compilation.args'):
            compilation.args = []

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

    async def compile_opendream(tenv):
        cenv = tenv.branch()

        cenv.attr.build.dir = cenv.attr.install.dir / 'DMCompiler'
        cenv.attr.process.stdout = open(cenv.attr.test.root_dir / 'opendream.compile.stdout.txt', "w")
        await DMShared.OpenDream.Compilation.compile( cenv )

        with open(cenv.attr.test.root_dir / "opendream.compile.returncode.txt", "w") as f:
            f.write( str(cenv.attr.compilation.returncode) )
        cenv.attr.process.stdout.close()

        return cenv

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