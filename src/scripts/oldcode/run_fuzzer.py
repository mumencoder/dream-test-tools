
from common import *

async def run_test(env):
    ctenv = env.merge( baseenv.attr.envs.byond )

    await DMTR.Runners.byond_codetree(ctenv)
    await DMTR.Runners.opendream_ast(ctenv)
    await DMTR.Runners.clopen_ast(ctenv)
    #await DMTR.Runners.run_meta(ctenv)

    return ctenv

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

def generate_n_tests(env, n):
    generated_test_count = 0
    c = 0
    print_c = [2 ** x for x in range(0,11)]
    start_time = time.time()
    while generated_test_count < n:
        tenv = env.branch()
        DMTR.Persist.try_init_test_instance(tenv)
        generate_test(tenv)
        yield tenv
        DMTR.Persist.save_test_dm(tenv)
        DMTR.Persist.save_test_ngrams(tenv)
        #save_collider_info(tenv)
        DMTR.Metadata.save_test(tenv)
        generated_test_count += 1
        c += 1
        if c % 1024 == 0 or c in print_c:
            print(f"{c} {c / (time.time() - start_time)} tests/sec")

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
    if DMTR.Persist.is_generated(tenv):
        await run_test(tenv)

async def run_test_batch(output_dir, path, tmp_path):
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
        if DMTR.Persist.is_generated(tenv):
            await run_test(tenv)
        c += 1
        if c % 1024 == 0 or c in print_c:
            print(f"{c} {c / (time.time() - start_time)} tests/sec")

async def ngram_report(output_dir, path):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )
    c = 0
    start_time = time.time()
    print_c = [2 ** x for x in range(0,11)]
    all_ngram_counts = DreamCollider.NGram.new_accum()
    for test_path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch()
        tenv.attr.test.root_dir = Shared.Path( test_path )
        DMTR.Metadata.load_test(tenv)
        DMTR.Results.process_test(tenv)
        if DMTR.Persist.is_generated(tenv):
            DreamCollider.NGram.accum_count(all_ngram_counts, tenv.attr.test.files.ngram_info)
        c += 1
        if c % 1024 == 0 or c in print_c:
            print(f"{c} {c / (time.time() - start_time)} tests/sec")

    print( all_ngram_counts["token_count"] )
    DreamCollider.NGram.bin_counts( all_ngram_counts["ngram_counts"] )

async def generate_batch(output_dir, path, n, *args):
    env = Shared.Environment()
    env.attr.tests.root_dir = Shared.Path( path )
    env.attr.tests.required_test_count = int(n)
    env.attr.ngrams = DreamCollider.NGram()

    if "reset" in args and os.path.exists( env.attr.tests.root_dir ):
        shutil.rmtree( env.attr.tests.root_dir )
    # count existing tests
    exist_test_count = len(list(DMTR.Persist.iter_existing_tests(env)))
    print( f"found {exist_test_count} existing tests" )
    # generate remaining
    tests_needed = env.attr.tests.required_test_count - exist_test_count
    for tenv in generate_n_tests(env, tests_needed):
        pass
    exist_test_count = len(list(DMTR.Persist.iter_existing_tests(env)))
    print( f"found {exist_test_count} existing tests" )

asyncio.run( globals()[sys.argv[1]]( *sys.argv[2:] ) )