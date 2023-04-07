
from common import *

def count_existing(env):
    return len(os.listdir( env.attr.churn.config.result_dir ))

def trim_tests(env, n):
    test_ids = os.listdir( env.attr.churn.config.result_dir )
    count = len(test_ids)
    print(f"trimming {count} tests")
    if count > 100000:
        keeps = test_ids[0:100000]
        for test_id in test_ids:
            if test_id not in keeps:
                shutil.rmtree( env.attr.churn.config.result_dir / test_id )

async def clear():
    root_env = base_env()

    load_churn(root_env, sys.argv[2])    

    root_env.attr.churn.config.result_dir.ensure_clean_dir()

async def churn():
    manager = mp.Manager()
    queue = manager.Queue()
    root_env = base_env()

    load_churn(root_env, sys.arg[2])    
    load_byond_install(root_env, "byond_main")

    async def worker_loop(queue):
        filters_finished = set()
        while True:
            tenv = root_env.branch()

            if len(tenv.attr.churn.filters) == len(filters_finished):
                return
            
            for builder in tenv.attr.churn.builders.values():
                await builder(tenv)
            generate_ast(tenv)
            tokenize_ast(tenv)
            unparse_tokens(tenv)
            for tester in tenv.attr.churn.testers.values():
                await tester(tenv)
            for filter_name, filter_fn in tenv.attr.churn.filters.items():
                if os.path.exists( tenv.attr.churn.config.result_dir / filter_name ):
                    if len( os.listdir( tenv.attr.churn.config.result_dir / filter_name ) ) > 100:
                        filters_finished.add( filter_name )
                if filter_name in filters_finished:
                    continue
                if await filter_fn(tenv):
                    data = save_test(tenv)
                    test_id = Shared.Random.generate_string(24)
                    with open( tenv.attr.churn.config.result_dir / filter_name / test_id, "wb" ) as f:
                        f.write( data )

    async def worker_task(queue):
        tasks = []
        tasks.append( asyncio.create_task(worker_loop(queue)) )
        tasks.append( asyncio.create_task(worker_loop(queue)) )
        while True:
            await asyncio.sleep(1.0)
            for t in tasks:
               if not t.done():
                   continue
            break

    def worker_process(queue):
        try:
            asyncio.run( worker_task(queue) )
        except KeyboardInterrupt:
            pass

    processes = []
    for i in range(0, 2):
        processes.append( mp.Process(target=worker_process, args=(queue,)) )
    for proc in processes:
        proc.start()

    last_print = time.time()
    while True:
        await asyncio.sleep(1.0)
        if time.time() - last_print > 120.0:
            print("churning...", time.time() )
            last_print = time.time()
        for p in processes:
            if p.is_alive():
                continue
        return
try:
    asyncio.run( globals()[sys.argv[1]]() )
except KeyboardInterrupt:
    pass