
from common import *

def count_existing(env):
    return len(os.listdir( env.attr.churn_dir ))

async def clear():
    root_env = base_env()
    root_env.attr.churn_dir.ensure_clean_dir()

def trim_tests(env):
    test_ids = os.listdir( env.attr.churn_dir )
    count = len(test_ids)
    print(f"trimming {count} tests")
    if count > 100000:
        keeps = test_ids[0:100000]
        for test_id in test_ids:
            if test_id not in keeps:
                shutil.rmtree( env.attr.churn_dir / test_id )

async def recompute():
    root_env = base_env()
    for test_id in os.listdir( root_env.attr.churn_dir ):
        tenv = root_env.branch()
        try:
            with open( root_env.attr.churn_dir / test_id / 'byond_compile.pickle', 'rb') as f:
                load_test(tenv, f.read() )
        except:
            continue
        DMShared.Byond.Compilation.parse_compile_stdout( tenv )
        with open( root_env.attr.churn_dir / test_id / 'byond_compile.pickle', 'wb') as f:
            f.write( save_test(tenv) )

async def churn_for_unknowns():
    q = mp.Queue()

    churn_ct = 0
    churn_start_time = time.time()

    async def worker_loop():
        nonlocal churn_ct
        root_env = base_env()
        while True:
            renv = await dmsource_all_tasks(root_env)
            for error in renv.attr.benv.attr.compile.stdout_parsed["errors"]:
                if error["category"] == "UNKNOWN":
                    test_id = Shared.Random.generate_string(24)
                    with open( root_env.attr.churn_dir / test_id / 'byond_compile.pickle', 'wb') as f:
                        f.write( save_test(renv.attr.benv) )
                    print("unknown generated")
                    break
            churn_ct += 1

    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    asyncio.create_task(worker_loop())
    while True:
        print(f"churned {churn_ct} tests, {churn_ct / (time.time()-churn_start_time)} sec")
        await asyncio.sleep(120.0)

async def churn():
    root_env = base_env()
    while True:
        renv = await dmsource_all_tasks(root_env)
        test_id = Shared.Random.generate_string(24)

        with open( root_env.attr.churn_dir / test_id / 'byond_compile.pickle', 'wb') as f:
            f.write( save_test(renv.attr.benv) )

        if random.random() < (1/10000.0):
            trim_tests(root_env)

asyncio.run( globals()[sys.argv[1]]() )