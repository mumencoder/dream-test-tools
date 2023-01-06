
from .common import *

from .Dotnet import clr

if import_dotnet:
    import ClopenDream
    import DMCompiler
    from DMCompiler.Compiler.DM import DMAST
    from System import *
    import System.Threading.Tasks
    import System.IO
    from System.Collections.Generic import List

async def compile_byond(tenv):
    cenv = tenv.branch()

    cenv.attr.process.stdout = open(tenv.attr.test.root_dir / 'byond.compile.stdout.txt', "w")
    await DMShared.Byond.Compilation.compile(cenv)
    with open(tenv.attr.test.root_dir / 'byond.compile.stdout.txt', "r") as f:
        cenv.attr.compilation.log = f.read()

    with open(tenv.attr.test.root_dir / "byond.compile.returncode.txt", "w") as f:
        f.write( str(cenv.attr.compilation.returncode) )
    cenv.attr.process.stdout.close()

    return cenv

async def byond_codetree(benv):
    tenv = benv.branch()
    tenv.attr.compilation.dm_file_path = tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file
    tenv.attr.compilation.args = ["code_tree"]
    await compile_byond(tenv)

    os.rename( tenv.attr.test.root_dir / 'byond.compile.stdout.txt', tenv.attr.test.root_dir / 'byond.codetree.stdout.txt')
    os.rename( tenv.attr.test.root_dir / 'byond.compile.returncode.txt', tenv.attr.test.root_dir / 'byond.codetree.returncode.txt')

    new_file_from_path( benv, 'byond_codetree_stdout', 'byond.codetree.stdout.txt')
    new_file_from_path( benv, 'byond_codetree_return', 'byond.codetree.returncode.txt')

async def run_byond(tenv, cenv):
    renv = None
    if cenv.attr.compilation.returncode == 0:
        renv = tenv.branch()
        renv.attr.run.exit_condition = DMShared.Byond.Run.wait_test_output
        renv.event_handlers['process.wait'] = DMShared.Byond.Run.wait_run_complete
        renv.attr.process.stdout = open(renv.attr.test.root_dir / 'byond.run.stdout.txt', "w")
        renv.attr.run.dm_file_path = DMShared.Byond.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        renv.attr.run.args = {'trusted':True}
        await DMShared.Byond.Run.run(renv)
        renv.attr.process.stdout.close()
        with open(renv.attr.test.root_dir / 'byond.run.stdout.txt', "r") as f:
            renv.attr.run.log = f.read()
        if os.path.exists( renv.attr.test.root_dir / 'test.out.json'):
            with open( renv.attr.test.root_dir / 'test.out.json', "r" ) as f:
                try:
                    renv.attr.run.output = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            os.remove( renv.attr.test.root_dir / 'test.out.json')

    return renv

async def prepare_empty(ienv, oenv):
    with open( ienv.attr.test.root_dir / 'empty.dm', "w") as f:
        f.write('')

    ienv.attr.compilation.dm_file_path = ienv.attr.test.root_dir / 'empty.dm'
    ienv.attr.compilation.args = ["code_tree"]
    await compile_byond(ienv)

    with open( ienv.attr.test.root_dir / 'byond.compile.stdout.txt', "r") as f:
        codetree = f.read()
    oenv.attr.empty.codetree = codetree

    p = ClopenDream.Parser()
    try:
        empty_root = p.BeginParse( System.IO.StringReader( oenv.attr.empty.codetree ) )
        empty_root.FixLabels()
    except Exception as e:
        print(e)
        for error in p.errors:
            print(error)
    oenv.attr.empty.root = empty_root

    l = List[System.String]()
    l.Add( str(ienv.attr.compilation.dm_file_path) )
    state = DMCompiler.DMCompiler.GetAST( l )

    oenv.attr.empty.open_compile = state

async def compile_opendream(tenv):
    cenv = tenv.branch()

    cenv.attr.build.dir = cenv.attr.install.dir / 'DMCompiler'
    cenv.attr.process.stdout = open(cenv.attr.test.root_dir / 'opendream.compile.stdout.txt', "w")
    await DMShared.OpenDream.Compilation.compile( cenv )

    with open(cenv.attr.test.root_dir / "opendream.compile.returncode.txt", "w") as f:
        f.write( str(cenv.attr.compilation.returncode) )
    cenv.attr.process.stdout.close()

    return cenv

async def clopen_ast(tenv):
    env = tenv.branch()
    codetree = System.IO.StringReader( env.attr.test.files.byond_codetree_stdout )

    result = ClopenDream.ClopenDream.PrepareAST( codetree, tenv.attr.empty.root )

    if "parser_exc" in result:
        tenv.attr.test.metadata.paths.clparser_throw = 'clparser_throw.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_throw, "w") as f:
            f.write( result["parser_exc"].StackTrace + '\n')
            f.write( "===\n" )
    else:
        if tenv.attr_exists( '.test.metadata.paths.clparser_throw' ):
            del tenv.attr.test.metadata.paths.clparser_throw

    if len(result["parser"].errors) > 0:
        tenv.attr.test.metadata.paths.clparser_errors = 'clparser_errors.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_errors, "w") as f:
            for error in result["parser"].errors:
                f.write( error + '\n' )
                f.write( "===\n" )
    else:
        if tenv.attr_exists( '.test.metadata.paths.clparser_errors' ):
            del tenv.attr.test.metadata.paths.clparser_errors

    if len(result["parser"].byond_errors) > 0:
        tenv.attr.test.metadata.paths.byond_errors = 'byond_errors.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.byond_errors, "w") as f:
            for error in result["parser"].byond_errors:
                f.write( error.Text + '\n' )
    else:
        if tenv.attr_exists( '.test.metadata.paths.byond_errors' ):
            del tenv.attr.test.metadata.paths.byond_errors

    if "root_node" in result and result["root_node"] is not None:
        tenv.attr.test.metadata.paths.clparser_tree = 'clparser_tree.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clparser_tree, "w") as f:
            f.write( result["root_node"].PrintLeaves(128) )
    else:
        if tenv.attr_exists( '.test.metadata.paths.clparser_tree' ):
            del tenv.attr.test.metadata.paths.clparser_tree

    if "convert_exc" in result:
        tenv.attr.test.metadata.paths.clconvert_throw = 'clconvert_throw.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_throw, "w") as f:
            f.write( result["convert_exc"].Source + '\n')
            f.write( result["convert_exc"].Message + '\n')
            f.write( result["convert_exc"].StackTrace + '\n')
            f.write( "===\n" )
    else:
        if tenv.attr_exists( '.test.metadata.paths.clconvert_throw' ):
            del tenv.attr.test.metadata.paths.clconvert_throw

    if len(result["converter"].errors) > 0:
        tenv.attr.test.metadata.paths.clconvert_errors = 'clconvert_errors.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.clconvert_errors, "w") as f:
            for error in result["converter"].errors:
                f.write( error + '\n' )
                f.write( "===\n" )
    else:
        if tenv.attr_exists( '.test.metadata.paths.clconvert_errors' ):
            del tenv.attr.test.metadata.paths.clconvert_errors

    Metadata.save_test(tenv)

async def run_meta(tenv):
    lexer = ClopenDream.DMLexer()
    get_file(tenv, 'dm_file')
    src = ClopenDream.SourceText( tenv.attr.test.files.dm_file )
    lexer.Include( src )

    parsing = True
    while parsing:
        token = lexer.NextToken()
        if token.K == ClopenDream.DMToken.Kind.EndOfFile:
            parsing = False
        print( token.ToString() )

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

async def run_opendream(tenv):
    cenv = tenv.branch()
    if cenv.attr.compilation.returncode == 0:
        renv = tenv.branch()
        renv.attr.build.dir = Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Server'
        renv.attr.process.stdout = open(renv.attr.test.root_dir / 'opendream.run.stdout.txt', "w")
        renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        renv.attr.run.args = {}
        await DMShared.OpenDream.Run.run(renv)
        renv.attr.process.stdout.close()
    return renv
    
async def setup_opendream_dotnet():
    savedir = os.getcwd()
    os.chdir( str( Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Tests' / 'DMProject' ) )
    tests = DMTests()
    tests.BaseSetup()
    tests.OneTimeSetup()
    os.chdir( savedir )
    dreamman = IoCManager.Resolve[IDreamManager]()

async def run_opendream_dotnet():
    cenv = tenv.branch()

    tenv.attr.shell.dir = tenv.attr.test.root_dir
    settings = DMCompilerSettings()
    settings.Files = List[String]()
    settings.Files.Add( str(tenv.attr.compilation.dm_file_path) )

    prevout = Console.Out
    stdout = System.IO.StringWriter(System.Text.StringBuilder())
    Console.SetOut(stdout)
    try:
        cenv.attr.compilation.returncode = DMCompiler.Compile(settings)
    except Exception as e:
        cenv.attr.compilation.returncode = False
    Console.SetOut(prevout)
    cenv.attr.compilation.log = stdout.ToString()
    with open( cenv.attr.test.root_dir / 'opendream.compile.stdout.txt', "w" ) as f:
        f.write( cenv.attr.compilation.log )

    renv = None
    if cenv.attr.compilation.returncode is True:
        renv = tenv.branch()
        renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        dreamman.LoadJson( str(renv.attr.run.dm_file_path) )

        try:
            t = tests.RunNewTest()
            success = t.Item1
            rval = t.Item2
            renv.attr.run.log = str(t.Item3)
        except Exception as e:
            pass

        if os.path.exists( renv.attr.test.root_dir / 'test.out.json'):
            with open( renv.attr.test.root_dir / 'test.out.json', "r" ) as f:
                try:
                    renv.attr.run.output = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            os.remove( renv.attr.test.root_dir / 'test.out.json')
    
    return (cenv, renv)

