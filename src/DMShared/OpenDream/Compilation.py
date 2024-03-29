
from ..common import *

class Compilation(object):
    @staticmethod
    def convert_args(env):
        if not env.has_attr('.compilation.args'):
            args = []
        s = []
        for arg in args:
            if type(arg) is dict and arg["type"] == "flags":
                for flag in arg["flags"]:
                    s.append( f"--{flag} " )

        s.append( env.attr.compilation.dm_file_path.name )
        return s

    @staticmethod
    def get_exe_path(env):
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.install.dir / 'DMCompiler'):
            for filename in files:
                if filename == "DMCompiler":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod
    def find_compiler_binary(env):
        exe_paths = Compilation.get_exe_path(env)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", env.attr.install.dir / 'DMCompiler', exe_paths)
        env.attr.opendream.compiler_binary = exe_paths[0]

    async def managed_compile(env):
        menv = env.branch()

        Shared.Process.pipe_stdout(menv)
        menv.attr.shell.dir = menv.attr.compilation.dm_file_path.parent
        menv.attr.shell.env = os.environ
        if not menv.has_attr('.opendream.compiler_binary'):
            Compilation.find_compiler_binary(menv)
        menv.attr.shell.program = menv.attr.opendream.compiler_binary
        menv.attr.shell.args = Compilation.convert_args(menv)
        await Shared.Process.shell(menv)

        env.attr.compile.stdout = menv.attr.process.stdout.getvalue()
        env.attr.compile.returncode = menv.attr.process.instance.returncode

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
            if tenv.has_attr( '.test.metadata.paths.opendream_errors' ):
                del tenv.attr.test.metadata.paths.opendream_errors

        warnings = DMCompiler.DMCompiler.warnings
        if warnings.Count > 0:
            tenv.attr.test.metadata.paths.opendream_warnings = 'opendream_warnings.txt'
            with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_warnings, "w") as f:
                for warning in warnings:
                    f.write( warning.ToString() + '\n')
        else:
            if tenv.has_attr( '.test.metadata.paths.opendream_warnings' ):
                del tenv.attr.test.metadata.paths.opendream_warnings

        Metadata.save_test(tenv)

    def parse_errors(text):
        for line in text.split('\n'):
            if not line.startswith("Error"):
                continue
            ss = line.split(" ")
            if len(ss) < 4:
                continue
            # TODO: this probably will not work for filename with spaces
            ff = ss[3].split(":")
            if len(ff) >= 2:
                yield {"file":ff[0].strip(), "lineno":int(ff[1]), "msg":" ".join(ss[3:]), "text":line }

    def opendream_errors_info( text ):
        info = {"lines": sorted(list(Display.opendream_errors(text)), key=lambda line: line["lineno"]) }
        info["lines"] = [ line for line in info["lines"] if line["file"] == 'test.dm' ]
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
        return info
    
    @staticmethod
    def error_category(err):
        msg = err["msg"]
        if 'Unknown identifier' in msg:
            return "UNDEF_VAR"
        if 'Invalid path' in msg:
            return 'UNDEF_TYPEPATH'
        if 'const operation' in msg and 'is invalid' in msg:
            return "EXPECTED_CONSTEXPR"
        if 'Unknown global' in msg:
            return "UNDEF_VAR"
        if 'Invalid initial value' in msg:
            return "INVALID_INIT"
        if 'proc' in msg and 'is already defined in global scope' in msg:
            return "DUPLICATE_GLOBAL_PROC"
        if 'Type' in msg and 'already has a proc named' in msg:
            return "DUPLICATE_OBJ_PROC"
        if 'Duplicate definition of static var' in msg:
            return "DUPLICATE_STATIC_VAR"
        if 'Duplicate definition of var' in msg:
            return "DUPLICATE_DEF"
        return 'UNKNOWN'