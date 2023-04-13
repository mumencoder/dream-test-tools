
from common import *

async def churn():
    manager = mp.Manager()
    queue = manager.Queue()
    root_env = base_env()

    load_churn(root_env, sys.argv[2])    

    root_env.attr.benv = root_env.branch()
    root_env.attr.oenv = root_env.branch()
    load_byond_install(root_env.attr.benv, "byond_main")
    load_opendream_install(root_env.attr.oenv, "opendream_current")

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
        running = True
        while running:
            await asyncio.sleep(1.0)
            running = False
            for t in tasks:
               if not t.done():
                   running = True

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
    running = True
    while running:
        await asyncio.sleep(1.0)
        if time.time() - last_print > 120.0:
            print("churning...", time.time() )
            last_print = time.time()
        running = False
        for p in processes:
            if p.is_alive():
                running = True
try:
    asyncio.run( globals()[sys.argv[1]]() )
except KeyboardInterrupt:
    pass