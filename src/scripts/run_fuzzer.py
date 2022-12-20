
from common import *

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
    DMTR.Metadata.load_test(env)

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
    tenv.attr.test.metadata.paths.collider_model = 'collider_model.json'
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "w") as f:
        source = builder.unparse()
        f.write( source )
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_model, "w") as f:
        f.write( json.dumps(builder.get_model(), cls=DreamCollider.ModelEncoder) )
    DMTR.Metadata.save_test(tenv)

async def run_test(env):
    ctenv = env.merge( baseenv.attr.envs.byond )

    await DMTR.Runners.byond_codetree(ctenv)
    #await DMTR.Runners.opendream_ast(ctenv)
    await DMTR.Runners.clopen_ast(ctenv)

    return ctenv

async def find_new_errors(path, tmp_path):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )
    if os.path.exists( env.attr.tests.root_dir ):
        shutil.rmtree( env.attr.tests.root_dir )

    # copy DMStandard and DLLs
    empenv = Shared.Environment()
    benv = baseenv.attr.envs.byond.branch()
    benv.attr.test.root_dir = Shared.Path( tmp_path ) / 'empty' 
    await DMTR.Runners.prepare_empty(benv, empenv)

    c = 0
    start_time = time.time()
    print_c = [2 ** x for x in range(0,11)]
    while True:
        tenv = env.branch().merge(empenv)
        try_init_test_instance(tenv)
        generate_test_and_save(tenv)
        if is_generated(tenv):
            await run_test(tenv)

        c += 1
        if c % 1024 == 0 or c in print_c:
            print(f"{c} {c / (time.time() - start_time)} tests/sec")

        shutil.rmtree( tenv.attr.test.root_dir )
        env.branches = []

async def run_single_test(test_path, tmp_path):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( test_path )

    # copy DMStandard and DLLs
    empenv = Shared.Environment()
    benv = baseenv.attr.envs.byond.branch()
    benv.attr.test.root_dir = Shared.Path( tmp_path ) / 'empty' 
    await DMTR.Runners.prepare_empty(benv, empenv)

    tenv = env.branch().merge(empenv)
    tenv.attr.test.root_dir = Shared.Path( test_path )
    DMTR.Metadata.load_test(tenv)
    if is_generated(tenv):
        await run_test(tenv)

async def run_test_batch(path, tmp_path):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )

    # copy DMStandard and DLLs
    empenv = Shared.Environment()
    benv = baseenv.attr.envs.byond.branch()
    benv.attr.test.root_dir = Shared.Path( tmp_path ) / 'empty' 
    await DMTR.Runners.prepare_empty(benv, empenv)

    c = 0
    start_time = time.time()
    print_c = [2 ** x for x in range(0,11)]
    for test_path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch().merge(empenv)
        tenv.attr.test.root_dir = Shared.Path( test_path )
        DMTR.Metadata.load_test(tenv)
        if is_generated(tenv):
            await run_test(tenv)
        c += 1
        if c % 1024 == 0 or c in print_c:
            print(f"{c} {c / (time.time() - start_time)} tests/sec")

async def generate_batch(path, n, *args):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )
    env.attr.tests.required_test_count = int(n)

    if "reset" in args:
        shutil.rmtree( env.attr.tests.root_dir )
    # count existing tests
    exist_test_count = 0
    for path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch()
        env.attr.test.root_dir = Shared.Path( path )
        DMTR.Metadata.load_test(tenv)
        if is_generated(tenv):
            exist_test_count += 1
    print( f"found {exist_test_count} existing tests" )
    current_test_count = exist_test_count
    # generate remaining
    generated_test_count = 0
    while current_test_count < env.attr.tests.required_test_count:
        tenv = env.branch()
        try_init_test_instance(tenv)
        generate_test_and_save(tenv)
        current_test_count += 1
        generated_test_count += 1
    print( f"generated {generated_test_count} tests")

asyncio.run( globals()[sys.argv[1]]( *sys.argv[2:] ) )