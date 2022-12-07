
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

def load_test_metadata(env):
    env.attr.test.metadata_path = env.attr.test.root_dir / 'test.metadata.json'
    if os.path.exists( env.attr.test.metadata_path ):
        with open(env.attr.test.metadata_path, "r") as f:
            md = json.load(f)
            for attr, value in md.items():
                env.properties[attr] = value

def save_test_metadata(env):
    env.attr.test.metadata_path = env.attr.test.root_dir / 'test.metadata.json'

    md = {}
    for attr in env.unique_properties():
        if attr.startswith( '.test.metadata.' ):
            md[attr] = env.properties[attr]

    with open( env.attr.test.metadata_path, "w" ) as f:
        f.write( json.dumps(md) )

def try_init_test_instance(env):
    env.attr.test.name = Shared.Random.generate_string(24)
    env.attr.test.root_dir = env.attr.tests.root_dir / env.attr.test.name
    load_test_metadata(env)

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

    save_test_metadata(tenv)

async def run_test(env):
    ctenv = env.merge( baseenv.attr.envs.byond )
    await byond_codetree(ctenv)

    codetree = System.IO.StringReader( ctenv.attr.test.byond_codetree )
    empty_codetree = System.IO.StringReader( env.attr.empty.codetree )
    empty_compile = env.attr.empty.open_compile

    output = System.IO.StringWriter()
    (result, clopen_ast) = ClopenDream.ClopenDream.PrepareAST( output, codetree, empty_codetree, empty_compile )
    if result is False:
        print( output.ToString() )

    env.attr.compilation.dm_file_path = env.attr.test.root_dir / env.attr.test.metadata.paths.dm_file
    l = List[System.String]()
    l.Add( str(env.attr.compilation.dm_file_path) )
    open_state = DMCompiler.DMCompiler.GetAST( l )

    # TODO: dump open errors

async def prepare_empty(ienv, oenv):
    with open( ienv.attr.test.root_dir / 'empty.dm', "w") as f:
        f.write('')

    ienv.attr.compilation.dm_file_path = ienv.attr.test.root_dir / 'empty.dm'
    ienv.attr.compilation.args = ["code_tree"]
    await DMTestRunner.compile_byond(ienv)

    with open( ienv.attr.test.root_dir / 'byond.compile.stdout.txt', "r") as f:
        codetree = f.read()

    l = List[System.String]()
    l.Add( str(ienv.attr.compilation.dm_file_path) )
    state = DMCompiler.DMCompiler.GetAST( l )

    oenv.attr.empty.codetree = codetree
    oenv.attr.empty.open_compile = state

async def byond_codetree(benv):
    tenv = benv.branch()
    tenv.attr.compilation.dm_file_path = tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file
    tenv.attr.compilation.args = ["code_tree"]
    await DMTestRunner.compile_byond(tenv)

    os.rename( tenv.attr.test.root_dir / 'byond.compile.stdout.txt', tenv.attr.test.root_dir / 'byond.codetree.stdout.txt')
    benv.attr.test.metadata.paths.codetree = 'byond.codetree.stdout.txt'
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
        load_test_metadata(tenv)
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
        load_test_metadata(tenv)
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