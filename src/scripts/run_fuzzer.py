
from common import *

baseenv = base_setup( Shared.Environment() )
#load_opendream(env.attr.envs.opendream)
load_clopendream(baseenv.attr.envs.clopendream)

import ClopenDream
import DMCompiler
from DMCompiler.Compiler.DM import DMAST
from System import *
import System.Threading.Tasks
import System.IO
from System.Collections.Generic import List

def generate_test():
    env = Shared.Environment()
    env.attr.expr.depth = 3
    builder = DreamCollider.FullRandomBuilder( )
    builder.generate( env )
    return builder

async def print_main():
    builder = generate_test()
    print("====================================")
    builder.print( sys.stdout )
    print("====================================")
    print( builder.unparse() )

async def print_many_main():
    for i in range(0, 10000):
        if i % 1000 == 0:
            print(i)
        builder = generate_test()
        if random.random() < 0.001:
            print("====================================")
            print( builder.unparse() )

def try_init_test_instance(env):
    env.attr.test.metadata.name = Shared.Random.generate_string(24)
    env.attr.test.root_dir = env.attr.tests.root_dir / env.attr.test.metadata.name
    DMTestRunner.Metadata.load_test(env)

def is_generated(env):
    if env.attr_exists('.test.metadata.paths.dm_file'):
        return True
    else:
        return False

def generate_test_and_save(tenv):
    if is_generated(tenv):
        return
    builder = generate_test()
    tenv.attr.test.metadata.paths.dm_file = 'test.dm'
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "w") as f:
        f.write( builder.unparse() )

    DMTestRunner.Metadata.save_test(tenv)

async def clopen_ast(tenv):
    env = tenv.branch()
    codetree = System.IO.StringReader( env.attr.test.byond_codetree )

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
                f.write( error.Test + '\n' )
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

    if "root_node" in result:
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
                f.write( error.Text + '\n' )
                f.write( "===\n" )
    else:
        if tenv.attr_exists( '.test.metadata.paths.clconvert_errors' ):
            del tenv.attr.test.metadata.paths.clconvert_errors

    DMTestRunner.Metadata.save_test(tenv)

async def opendream_ast(tenv):
    env = tenv.branch()
    env.attr.compilation.dm_file_path = env.attr.test.root_dir / env.attr.test.metadata.paths.dm_file

    l = List[System.String]()
    l.Add( str(env.attr.compilation.dm_file_path) )
    tenv.attr.test.open_compile = DMCompiler.DMCompiler.GetAST( l )

    #DMAST.DMASTNodePrinter().Print(tenv.attr.test.open_compile.ast, System.Console.Out)
    errors = DMCompiler.DMCompiler.errors
    if errors.Count > 0:
        tenv.attr.test.metadata.paths.opendream_errors = 'opendream_errors.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.opendream_errors, "w") as f:
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

    DMTestRunner.Metadata.save_test(tenv)

async def run_test(env):
    ctenv = env.merge( baseenv.attr.envs.byond )
    await byond_codetree(ctenv)
    await clopen_ast(ctenv)
    await opendream_ast(ctenv)

async def prepare_empty(ienv, oenv):
    with open( ienv.attr.test.root_dir / 'empty.dm', "w") as f:
        f.write('')

    ienv.attr.compilation.dm_file_path = ienv.attr.test.root_dir / 'empty.dm'
    ienv.attr.compilation.args = ["code_tree"]
    await DMTestRunner.compile_byond(ienv)

    with open( ienv.attr.test.root_dir / 'byond.compile.stdout.txt', "r") as f:
        codetree = f.read()
    oenv.attr.empty.codetree = codetree

    p = ClopenDream.Parser()
    empty_root = p.BeginParse( System.IO.StringReader( oenv.attr.empty.codetree ) )
    empty_root.FixLabels()
    oenv.attr.empty.root = empty_root

    l = List[System.String]()
    l.Add( str(ienv.attr.compilation.dm_file_path) )
    state = DMCompiler.DMCompiler.GetAST( l )

    oenv.attr.empty.open_compile = state

async def byond_codetree(benv):
    tenv = benv.branch()
    tenv.attr.compilation.dm_file_path = tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file
    tenv.attr.compilation.args = ["code_tree"]
    await DMTestRunner.compile_byond(tenv)

    os.rename( tenv.attr.test.root_dir / 'byond.compile.stdout.txt', tenv.attr.test.root_dir / 'byond.codetree.stdout.txt')
    os.rename( tenv.attr.test.root_dir / 'byond.compile.returncode.txt', tenv.attr.test.root_dir / 'byond.codetree.returncode.txt')
    benv.attr.test.metadata.paths.codetree = 'byond.codetree.stdout.txt'
    benv.attr.test.metadata.paths.codetree_return = 'byond.codetree.returncode.txt'
    with open( tenv.attr.test.root_dir / benv.attr.test.metadata.paths.codetree, "r") as f:
        benv.attr.test.byond_codetree = f.read()

async def run_test_batch(path, tmp_path):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )

    # copy DMStandard and DLLs
    empenv = Shared.Environment()
    benv = baseenv.attr.envs.byond.branch()
    benv.attr.test.root_dir = Shared.Path( tmp_path ) / 'empty' 
    await prepare_empty(benv, empenv)

    for path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch().merge(empenv)
        tenv.attr.test.root_dir = Shared.Path( path )
        DMTestRunner.Metadata.load_test(tenv)
        if is_generated(tenv):
            await run_test(tenv)

async def generate_batch(path, n, *args):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )
    env.attr.tests.required_test_count = int(n)
    # count existing tests
    current_test_count = 0
    for path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch()
        env.attr.test.root_dir = Shared.Path( path )
        DMTestRunner.Metadata.load_test(tenv)
        if is_generated(tenv):
            current_test_count += 1
    print( f"found {current_test_count} existing tests" )
    # generate remaining
    while current_test_count < env.attr.tests.required_test_count:
        builder = generate_test()
        tenv = env.branch()
        try_init_test_instance(tenv)
        generate_test_and_save(tenv)
        current_test_count += 1

asyncio.run( globals()[sys.argv[1]]( *sys.argv[2:] ) )