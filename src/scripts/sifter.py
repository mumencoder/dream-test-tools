
from common import *

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
    if os.path.exists( env.attr.sifter.metadata_dir / 'sifter.json'):
        shutil.copy(env.attr.sifter.metadata_dir / 'sifter.json', env.attr.sifter.metadata_dir / 'sifter.json.backup' )
    with open(env.attr.sifter.metadata_dir / 'sifter.json', "w") as f:
        f.write( json.dumps( env.attr.sifter.metadata ) )
    load_sifter(env)

def iter_chunk_tests(env):
    for test_name in env.attr.sifter.chunk.tests:
        tenv = env.branch()
        tenv.attr.test.root_dir = env.attr.sifter.chunk.tests_dir / test_name
        DMTR.Persist.load_test(tenv)
        if DMTR.Persist.is_generated(tenv):
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

def iter_sifter_tests(env):
    for k, chunks in env.attr.sifter.metadata["chunk_index"].items():
        for chunk_id in chunks:
            with open( env.attr.sifter.chunk_dir / chunk_id, "r") as f:
                chunk_info = json.loads( f.read() )
                for test in chunk_info["tests"]:
                    yield test

def clean_chunks(env):
    known_chunks = set()
    for k, chunks in env.attr.sifter.metadata["chunk_index"].items():
        for chunk_id in chunks:
            known_chunks.add( chunk_id )

    removed_chunks = 0
    for chunk_file in os.listdir( env.attr.sifter.chunk_dir ):
        if chunk_file not in known_chunks:
            os.remove( env.attr.sifter.chunk_dir / chunk_file )
            removed_chunks += 1
    print(f"removed {removed_chunks} chunks")

def clean_tests(env):
    cleaned = 0
    start_time = time.time()
    known_tests = set( iter_sifter_tests(env))
    for test_dir in os.listdir(env.attr.sifter.metadata["tests_dir"]):
        if test_dir not in known_tests:
            shutil.rmtree( env.attr.sifter.metadata["tests_dir"] / test_dir )
            cleaned += 1
    print(f"cleaned {cleaned} tests in {time.time()-start_time}")

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

    clean_tests(env)
    clean_chunks(env)

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
                if random.random() < 4.0 / sifter["chunk_size"]:
                    print("===")
                    print( tenv.attr.collider.builder.text )
                    print("===")
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
            for i in range(0,20):
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
                clean_tests(env)
                clean_chunks(env)
            else:
                must_generate = True