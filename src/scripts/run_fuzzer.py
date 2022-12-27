
from common import *

def is_generated(env):
    if env.attr_exists('.test.metadata.paths.dm_file'):
        return True
    else:
        return False

def generate_test(tenv):
    if is_generated(tenv):
        return
    benv = Shared.Environment()
    benv.attr.expr.depth = 3
    builder = DreamCollider.FullRandomBuilder( )
    builder.generate( benv )
    builder.unparse(ngrams=tenv.attr.ngrams)
    tenv.attr.collider.builder = builder

def try_init_test_instance(env):
    env.attr.test.metadata.name = Shared.Random.generate_string(24)
    env.attr.test.root_dir = env.attr.tests.root_dir / env.attr.test.metadata.name
    DMTR.Metadata.load_test(env)

def save_test_dm(tenv):
    tenv.attr.test.metadata.paths.dm_file = 'test.dm'
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "w") as f:
        f.write( tenv.attr.collider.builder.text )

def save_test_ngrams(tenv):
    tenv.attr.test.metadata.paths.ngram_info = 'ngram_info.json'
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.ngram_info, "w") as f:
        f.write( json.dumps( tenv.attr.collider.builder.ngram_info ) )

def save_collider_info(tenv):
    tenv.attr.test.metadata.paths.collider_ast = 'collider_ast.txt'
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_ast, "w") as f:
        s = io.StringIO()
        tenv.attr.collider.builder.print(s)
        f.write( s.getvalue() )

    tenv.attr.test.metadata.paths.collider_model = 'collider_model.json'
    with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_model, "w") as f:
        f.write( json.dumps(tenv.attr.collider.builder.get_model(), cls=DreamCollider.ModelEncoder) )

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

def iter_existing_tests(env):
    for path, dirs, files in os.walk(env.attr.tests.root_dir):
        tenv = env.branch()
        tenv.attr.test.root_dir = Shared.Path( path )
        DMTR.Metadata.load_test(tenv)
        if is_generated(tenv):
            yield tenv

def generate_n_tests(env, n):
    generated_test_count = 0
    c = 0
    print_c = [2 ** x for x in range(0,11)]
    start_time = time.time()
    while generated_test_count < n:
        tenv = env.branch()
        try_init_test_instance(tenv)
        generate_test(tenv)
        yield tenv
        save_test_dm(tenv)
        save_test_ngrams(tenv)
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
    if is_generated(tenv):
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
        if is_generated(tenv):
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
        if is_generated(tenv):
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
    exist_test_count = len(list(iter_existing_tests(env)))
    print( f"found {exist_test_count} existing tests" )
    # generate remaining
    tests_needed = env.attr.tests.required_test_count - exist_test_count
    for tenv in generate_n_tests(env, tests_needed):
        pass
    exist_test_count = len(list(iter_existing_tests(env)))
    print( f"found {exist_test_count} existing tests" )

class Sifter(object):
    def __init__(self):
        pass

async def create_sifter(output_dir, metadata_dir, tests_dir, tests_target_count):
    env = Shared.Environment()
    env.attr.sifter.metadata_dir = Shared.Path( metadata_dir )
    tests_target_count = int(tests_target_count)

    chunk_size = tests_target_count / (2**4)
    if chunk_size != round(chunk_size):
        raise Exception(f"bad chunk size {chunk_size}, test target: {tests_target_count}")
    chunk_size = round(chunk_size)

    sifter = {
        "tests_dir":tests_dir,
        "test_target_count":tests_target_count,
        "chunk_size": chunk_size,
        "chunk_index": {}
    }
    env.attr.sifter.metadata = sifter
    save_sifter(env)

def load_sifter(env):
    env.attr.sifter.metadata["tests_dir"] = Shared.Path( env.attr.sifter.metadata["tests_dir"] )
    env.attr.sifter.metadata["chunk_size"] = int( env.attr.sifter.metadata["chunk_size"] )
    chunk_index = collections.defaultdict(list)
    chunk_index.update( env.attr.sifter.metadata["chunk_index"] )
    env.attr.sifter.metadata["chunk_index"] = chunk_index

def save_sifter(env):
    env.attr.sifter.metadata["tests_dir"] = str( env.attr.sifter.metadata["tests_dir"] )
    shutil.copy(env.attr.sifter.metadata_dir / 'sifter.json', env.attr.sifter.metadata_dir / 'sifter.json.backup' )
    with open(env.attr.sifter.metadata_dir / 'sifter.json', "w") as f:
        f.write( json.dumps( env.attr.sifter.metadata ) )
    load_sifter(env)

def iter_chunk_tests(env):
    for test_name in env.attr.sifter.chunk.tests:
        tenv = env.branch()
        tenv.attr.test.root_dir = env.attr.sifter.chunk.tests_dir / test_name
        DMTR.Metadata.load_test(tenv)
        if is_generated(tenv):
            yield tenv

def save_chunk(env):
    chunk_info = {"uuid": env.attr.sifter.chunk.uuid }
    chunk_info["tests_dir"] = str(env.attr.sifter.chunk.tests_dir)
    chunk_info["tests"] = env.attr.sifter.chunk.tests
    chunk_info["level"] = env.attr.sifter.chunk.level
    chunk_info["ngram_counts"] = env.attr.sifter.chunk.ngram_counts
    chunk_info["test_count"] = env.attr.sifter.chunk.test_count

    env.attr.sifter.chunk.file = env.attr.sifter.chunk_dir / env.attr.sifter.chunk.uuid
    with open( env.attr.sifter.chunk.file, "w") as f:
        f.write( json.dumps( chunk_info ) )

def load_chunk(env):
    env.attr.sifter.chunk.file = env.attr.sifter.chunk_dir / env.attr.sifter.chunk.uuid
    with open( env.attr.sifter.chunk.file, "r") as f:
        chunk_info = json.loads( f.read() )

    env.attr.sifter.chunk.uuid = chunk_info["uuid"]
    env.attr.sifter.chunk.tests_dir = Shared.Path( chunk_info["tests_dir"] )
    env.attr.sifter.chunk.tests = chunk_info["tests"] 
    env.attr.sifter.chunk.level = chunk_info["level"]
    env.attr.sifter.chunk.ngram_counts = chunk_info["ngram_counts"]
    env.attr.sifter.chunk.test_count = chunk_info["test_count"]

def merge_chunks(env, chunk1_id, chunk2_id):
    merge_accum = DreamCollider.NGram.new_accum()
    c1env = env.branch()
    c1env.attr.sifter.chunk.uuid = chunk1_id 
    load_chunk(c1env)
    c2env = env.branch()
    c2env.attr.sifter.chunk.uuid = chunk2_id
    load_chunk(c2env)
    DreamCollider.NGram.accum_count( merge_accum, c1env.attr.sifter.chunk.ngram_counts )
    DreamCollider.NGram.accum_count( merge_accum, c2env.attr.sifter.chunk.ngram_counts )

    pooled_tests = []
    for tenv in iter_chunk_tests(c1env):
        DMTR.Results.process_test(tenv)
        score = DreamCollider.NGram.score_test( merge_accum, tenv.attr.test.files.ngram_info )
        pooled_tests.append( {"tenv": tenv, "score":score} )
    for tenv in iter_chunk_tests(c2env):
        DMTR.Results.process_test(tenv)
        score = DreamCollider.NGram.score_test( merge_accum, tenv.attr.test.files.ngram_info )
        pooled_tests.append( {"tenv": tenv, "score":score } )

    import statistics
    scores = [entry["score"] for entry in pooled_tests]
    mean = statistics.mean( scores )
    stdev = statistics.stdev( scores )
    z_idx = collections.defaultdict(list)
    for entry in pooled_tests:
        entry["z"] = int(5 * (entry["score"] - mean) / stdev)
        z_idx[ entry["z"] ].append( entry )

    passing_tests = []
    for z, entries in sorted(z_idx.items(), key=lambda e: e[0], reverse=True):
        passing_tests += entries
        if len(passing_tests) > env.attr.sifter.metadata["chunk_size"]:
            break
    passing_tests = passing_tests[:env.attr.sifter.metadata["chunk_size"]]
    #print( statistics.mean( [entry["z"] for entry in passing_tests] ) )

    return {"tests":passing_tests, "accum": merge_accum}

async def run_sifter(output_dir, metadata_dir):
    env = Shared.Environment()
    env.attr.sifter.metadata_dir = Shared.Path( metadata_dir )
    env.attr.sifter.chunk_dir = env.attr.sifter.metadata_dir / 'chunks'
    env.attr.ngrams = DreamCollider.NGram()
    with open(env.attr.sifter.metadata_dir / 'sifter.json', "r") as f:
        env.attr.sifter.metadata = json.loads( f.read() )
        load_sifter(env)
        sifter = env.attr.sifter.metadata
    env.attr.tests.root_dir = sifter["tests_dir"]

    env.attr.sifter.total_tests = 0
    for k, chunks in sifter["chunk_index"].items():
        for chunk_id in chunks:
            with open( env.attr.sifter.chunk_dir / chunk_id, "r") as f:
                chunk_info = json.loads( f.read() )
                env.attr.sifter.total_tests += chunk_info["test_count"]

    must_generate = False    
    while True:
        env.branches = []
        if must_generate is True or env.attr.sifter.total_tests < sifter["test_target_count"]:
            cenv = env.branch()
            cenv.attr.sifter.chunk.uuid = Shared.Random.generate_string(24)
            cenv.attr.sifter.chunk.tests_dir = sifter["tests_dir"]
            cenv.attr.sifter.chunk.tests = []
            cenv.attr.sifter.chunk.level = 0
            cenv.attr.sifter.chunk.ngram_counts = DreamCollider.NGram.new_accum()
            cenv.attr.sifter.chunk.test_count = 0
            for tenv in generate_n_tests(cenv, sifter["chunk_size"]):
                cenv.attr.sifter.chunk.tests.append( tenv.attr.test.metadata.name )
                cenv.attr.sifter.chunk.test_count  += 1
                DreamCollider.NGram.accum_count(cenv.attr.sifter.chunk.ngram_counts, tenv.attr.collider.builder.ngram_info)
            save_chunk(cenv)
            if cenv.attr.sifter.chunk.test_count != sifter["chunk_size"]:
                raise Exception("chunk size incorrect")
            sifter["chunk_index"]["0"].append( cenv.attr.sifter.chunk.uuid )
            env.attr.sifter.total_tests += cenv.attr.sifter.chunk.test_count
            save_sifter(env)
            must_generate = False
        else:
            merge_result = None
            for i in range(0,12):
                i = str(i)
                if i in sifter["chunk_index"]:
                    chunks = sifter["chunk_index"][i]
                    if len(chunks) < 2:
                        continue
                else:
                    sifter["chunk_index"][i] = []
                    continue

                chunk1 = random.choice(chunks)
                chunk2 = random.choice(chunks)
                while chunk1 == chunk2:
                    chunk2 = random.choice(chunks)

                merge_result = merge_chunks(env, chunk1, chunk2)
                break
            if merge_result:
                cenv = env.branch()
                cenv.attr.sifter.chunk.uuid = Shared.Random.generate_string(24)
                cenv.attr.sifter.chunk.tests_dir = sifter["tests_dir"]
                cenv.attr.sifter.chunk.tests = []
                cenv.attr.sifter.chunk.level = int(i) + 1
                cenv.attr.sifter.chunk.ngram_counts = merge_result["accum"]
                cenv.attr.sifter.chunk.test_count = len(merge_result["tests"])
                for test in merge_result["tests"]:
                    tenv = test["tenv"]
                    cenv.attr.sifter.chunk.tests.append( tenv.attr.test.metadata.name )
                save_chunk(cenv)
                sifter["chunk_index"][i].remove( chunk1 )
                sifter["chunk_index"][i].remove( chunk2 )
                sifter["chunk_index"][str(cenv.attr.sifter.chunk.level)].append( cenv.attr.sifter.chunk.uuid )
                save_sifter(env)
                env.attr.sifter.total_tests -= cenv.attr.sifter.chunk.test_count
            else:
                must_generate = True


asyncio.run( globals()[sys.argv[1]]( *sys.argv[2:] ) )