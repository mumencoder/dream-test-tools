
import fastapi
import fastapi.security.api_key as apiseckey

from common import *

app = fastapi.FastAPI()

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

@app.post("/ast_gen")
async def ast_gen(request : fastapi.Request):
    env = root_env.branch()
    env.attr.pile.id = Shared.Random.generate_string(24)

    data = json.loads( gzip.decompress( await request.body() ) )
    for test in data["tests"]:
        test["id"] = Shared.Random.generate_string(24)

    env.attr.pile.data = data
    DMShared.PileArchive.Pile.save(env)

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
    root_env = base_env()

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
            update_cache()
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
