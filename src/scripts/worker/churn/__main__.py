
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

def clear(env):
    env.attr.churn.config.result_dir.ensure_clean_dir()

def parse_csv(l):
    return [ s.strip() for s in l.split(',') if s.strip() != "," ]

async def churn():
    churn_ct = 0
    churn_start_time = time.time()

    manager = mp.Manager()
    queue = manager.Queue()
    root_env = base_env()
    
    root_env.attr.verbose = False
    root_env.attr.churn.config = root_env.attr.config.prefix(f".{sys.argv[2]}")
    root_env.attr.churn.builders = { s:globals()[f'builder_{s}'] for s in parse_csv(root_env.attr.churn.config.builder) }
    root_env.attr.churn.testers = { s: globals()[f'tester_{s}'] for s in parse_csv(root_env.attr.churn.config.tester) }
    root_env.attr.churn.filters = { s: globals()[f'filter_{s}'] for s in parse_csv(root_env.attr.churn.config.filter) }

    async def worker_loop(queue):
        while True:
            tenv = root_env.branch()
            for builder in tenv.attr.churn.builders.values():
                await builder(tenv)
            generate_ast(tenv)
            tokenize_ast(tenv)
            unparse_tokens(tenv)
            for tester in tenv.attr.churn.testers.values():
                await tester(tenv)
            for filter_name, filter_fn in tenv.attr.churn.filters.items():
                if await filter_fn(tenv):
                    pass
            await asyncio.sleep(1.0)

            print("loop")

    async def worker_task(queue):
        asyncio.create_task(worker_loop(queue))
        asyncio.create_task(worker_loop(queue))
        while True:
            await asyncio.sleep(1.0)

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
        if time.time() - last_print > 120.0:
            print(f"churned {churn_ct} tests, {churn_ct / (time.time()-churn_start_time)} sec")
            last_print = time.time()
            root_env.attr.collider.build_checker.print_stat_freq()
        build_stats = queue.get()
        root_env.attr.collider.build_checker.add_check_result( build_stats )
        churn_ct += 1

        if random.random() < (1/10000.0):
            trim_tests(root_env)

try:
    asyncio.run( globals()[sys.argv[1]]() )
except KeyboardInterrupt:
    pass