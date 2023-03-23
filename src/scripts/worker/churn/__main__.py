
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
    churn_ct = 0
    churn_start_time = time.time()

    manager = mp.Manager()
    queue = manager.Queue()
    
    async def worker_loop(queue):
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
            queue.put(1)

    async def worker_task(queue):
        asyncio.create_task(worker_loop(queue))
        asyncio.create_task(worker_loop(queue))
        while True:
            await asyncio.sleep(1.0)

    def worker_process(queue):
        asyncio.run( worker_task(queue) )

    nproc = int(sys.argv[2])
    processes = []
    for i in range(0, nproc):
        processes.append( mp.Process(target=worker_process, args=(queue,)) )
    for proc in processes:
        proc.start()

    last_print = time.time()
    while True:
        if time.time() - last_print > 120.0:
            print(f"churned {churn_ct} tests, {churn_ct / (time.time()-churn_start_time)} sec")
            last_print = time.time()
        queue.get()
        churn_ct += 1

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