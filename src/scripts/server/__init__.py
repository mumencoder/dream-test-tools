
import fastapi
import fastapi.security.api_key as apiseckey

from common import *

app = fastapi.FastAPI()
root_env = base_env()

redis_conn = redis.Redis(host="redis")
work_queue = rq.Queue(connection=redis_conn)
job_index = {}

api_key_header = apiseckey.APIKeyHeader(name="x-auth-key", auto_error=False)
api_key_query = apiseckey.APIKeyQuery(name="auth", auto_error=False)

def check_api_key(
    api_key_query: str = fastapi.Security(api_key_query),
    api_key_header: str = fastapi.Security(api_key_header),
):
    if api_key_query in api_keys:
        return api_key_query
    if api_key_header in api_keys:
        return api_key_header
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
    
@app.get("/home")
async def home(request : fastapi.Request, api_key = fastapi.Security(check_api_key)):
    pass

@app.get("/action/{action_name}/{resource_name}")
async def action(action_name : str, resource_name : str, request : fastapi.Request):
    env = root_env.branch()
    rtype = root_env.attr.config_file['resources'][resource_name]['type']
    if rtype == 'opendream_repo':
        install_id = resource_name
        load_opendream_install(env, install_id)
    if rtype == 'churn':
        churn_id = resource_name
        load_churn(env, churn_id)
    if action_name == 'clear_churn':
        env.attr.churn.config.result_dir.ensure_clean_dir()
    if action_name == "start_churn":
        job_uuid = (resource_name, "churn")
        jstat = job_status(job_index, job_uuid)
        if jstat not in ["finished", "failed"]:
            return
        job = rq.job.Job.create(churn_run, [resource_name], timeout='48h', connection=redis_conn)
        work_queue.enqueue_job(job)
        job_index[(resource_name, "churn")] = job
    if action_name == 'clone':
        await Shared.Git.Repo.clone(env)
    if action_name == 'pull':
        await Shared.Git.Repo.pull(env)
    if action_name == 'build':
        env = env.branch()
        await DMShared.OpenDream.Builder.build(env)
        if env.attr.restore_env.attr.process.instance.returncode != 0:
            return
        if env.attr.compiler_env.attr.process.instance.returncode != 0:
            return
        if env.attr.server_env.attr.process.instance.returncode != 0:
            return
        status = await Shared.Git.Repo.status(env)
        metadata = maybe_from_pickle( get_file(env.attr.metadata_dir / 'resources' / install_id), default_value={} )
        metadata['last_build_commit'] = status['branch.oid']
        put_file( env.attr.metadata_dir / 'resources' / install_id, pickle.dumps(metadata) )
    if action_name == 'submodule_init':
        await Shared.Git.Repo.init_all_submodules(env)

@app.get("/installs/list")
async def installs(request : fastapi.Request):
    env = root_env.branch()
    def is_install_type(rtype):
        return rtype in ["byond_install", "opendream_repo"]
    
    resources = {}
    for resource_name, resource in root_env.attr.config_file['resources'].items():
        if not is_install_type(resource['type']):
            continue

        result = {}
        result["state"] = await globals()[f"status_{resource['type']}"](env, resource_name)
        result["resource"] = resource
        resources[resource_name] = result

    return resources

@app.get("/churn/list")
async def churn_list(request : fastapi.Request):
    churn_infos = {}
    for resource_name, resource in root_env.attr.config_file['resources'].items():
        if resource['type'] != 'churn':
            continue
        result = {}

        job_uuid = (resource_name, "churn")
        job = job_index.get(job_uuid, None)
        if job is not None:
            result["output"] = job.result
            if job.exc_info is not None:
                result["exc"] = str(job.exc_info)
        jstat = job_status(job_index, job_uuid)
        result["status"] = jstat

        churn_infos[resource_name] = result
    return churn_infos

@app.get("/churn/view/{name}")
async def churn_view(name : str, request : fastapi.Request):
    env = root_env.branch()
    out_env = Shared.Environment()
    load_churn_info(env.attr.config.prefix(f".{name}"), out_env)
    return env_tod( out_env, {} )

@app.get("/churn/view_test/{name}/{filter}/{test_id}")
async def churn_view_test(name : str, filter : str, test_id : str, request : fastapi.Request):
    env = root_env.branch()
    config = env.attr.config.prefix(f".{name}")
    load_churn_info(config, env)

    if not os.path.exists( config.result_dir / filter / test_id ):
        return None

    with open( config.result_dir / filter / test_id, "rb" ) as f:
        return fastapi.Response(f.read())
    
@app.get("/random_test/{category}")
def get_random_test(category : str, request : fastapi.Request):
    if len( test_ids_by_error_category[category] ) == 0:
        return None
    return json.dumps( random.choice( test_ids_by_error_category[category] ) )

@app.get("/error_counts")
def get_error_counts(request : fastapi.Request):
    return json.dumps(error_counts)

def update_cache():
    print("building cache...")
    t = time.time()

    new_error_counts = collections.defaultdict(int)
    new_test_ids_by_error_category = collections.defaultdict(list)
    for test_id in os.listdir( root_env.attr.churn_dir ):
        tenv = root_env.branch()

        try:
            with open( root_env.attr.churn_dir / test_id / 'byond_compile.pickle', "rb") as f:
                load_test(tenv, f.read())
            for error in tenv.attr.compile.stdout_parsed["errors"]:
                test_ids = new_test_ids_by_error_category[error['category']]
                if test_id not in test_ids:
                    new_test_ids_by_error_category[error['category']].append( test_id )
                new_error_counts[error['category']] += 1
        except:
            pass

    global error_counts, test_ids_by_error_category
    error_counts = new_error_counts
    test_ids_by_error_category = new_test_ids_by_error_category
    print(f"done! {time.time() - t} sec")

ticker = None
running = True
error_counts = collections.defaultdict(int)
test_ids_by_error_category = collections.defaultdict(list)

def server_tick():
    cache_update = None
    while running:
        if cache_update is None or time.time() - cache_update > 1800.0:
            #update_cache()
            cache_update = time.time()
        time.sleep(1.0)

@app.on_event("startup")
async def on_startup():
    global ticker
    ticker = threading.Thread(target=server_tick)
    ticker.start()

@app.on_event("shutdown")
async def on_startup():
    global running, ticker
    running = False
    ticker.join()
