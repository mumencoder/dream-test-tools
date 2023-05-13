
#### inactive misc code

### tasks
def new_task(fn, *args, **kwargs):
    pending_tasks.append( (fn, args, kwargs) )

def async_thread_launch():
    asyncio.run( async_thread_main() )

async def async_thread_main():
    global pending_tasks, tasks
   
    while True:
        for fn, args, kwargs in pending_tasks:
            tasks.add( asyncio.create_task( fn(*args, **kwargs) ) )
        pending_tasks = []

        try:
            for co in asyncio.as_completed(tasks, timeout=0.1):
                await co
        except TimeoutError:
            pass
        
        remaining_tasks = set()
        for task in tasks:
            if not task.done():
                remaining_tasks.add( task )
            else:
                pass
        tasks = remaining_tasks

## progress

class Counter(object):
    def __init__(self):
        self.c = 0
        self.visible_states = [2 ** x for x in range(0,11)]
        self.visible = False

    def inc(self, n=1):
        self.c += n
        self.update_state()
        
    def update_state(self):
        if self.c in self.visible_states or self.c % self.visible_states[-1] == 0:
            self.visible = True
        else:
            self.visible = False

    def state(self):
        return self.visible
    
#### inactive client code
def render_churn():
    churn_results = api_request('/churn/list').json()

    contents = []
    for name, result in churn_results.items():
        contents += [ 
            html.H3(name), 
            dcc.Link("View Results", href=f"/churn/view/{name}"), html.Br(),
            f"Job status: {result['status']}", html.Br(),
        ]
        if "output" in result:
            contents += [ f"Results:", html.Br(), html.Pre(result["output"]), html.Br() ]
        if "exc" in result:
            contents += [ f"Exception:", html.Br(), html.Pre(result["exc"]), html.Br() ]
        contents += [
            html.Button('Clear', id={'role':'action-btn', 'action':'clear_churn', 'resource':name} ),
            html.Button('Start', id={'role':'action-btn', 'action':'start_churn', 'resource':name} ),
            html.Hr(),
        ]

    return html.Div( contents )

def render_churn_view(m):
    churn_results = api_request( f"/churn/view/{m['name']}").json()
    env = env_fromd( Shared.Environment(), churn_results )

    contents = []
    for filter_name in env.attr.churn.filters:
        contents += [ html.Div(html.H2(filter_name)), html.Br() ]
        if filter_name not in env.attr.churn.filter_test_ids:
            return None
        for test_id in env.attr.churn.filter_test_ids[filter_name]:
            contents += [ dcc.Link(test_id, href=f"/churn/view_test/{m['name']}/{filter_name}/{test_id}"), html.Br() ]
    return html.Div(contents)

def render_churn_view_test(m):
    env = load_test( Shared.Environment(), api_request( f"/churn/view_test/{m['name']}/{m['filter']}/{m['test_id']}").content )
    contents = [html.Pre(env.attr.collider.text)]
    contents += [html.Hr(), html.H4("Compile returncode"), str(env.attr.byond.compile.returncode)]
    contents += [html.Br(), html.H4("Output:"), html.Pre(env.attr.byond.compile.stdout_text)]
    return html.Div(contents)

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
    
def render_any_from_category(category):
    root_env = base_env()

    result = api_request( f'/random_test/{category}').json()
    if result is None:
        return []
    test_id = json.loads( result )

    tenv = root_env.branch()
    with open( tenv.attr.churn_dir / test_id / 'byond_compile.pickle', "rb") as f:
        load_test(tenv, f.read())
    pp = pprint.PrettyPrinter(indent=2)
    return html.Div([
        html.Pre(tenv.attr.collider.text),
        html.Hr(),
        html.Pre(tenv.attr.compile.stdout_text),
        html.Hr(),
        html.Pre(tenv.attr.objtree.stdout_text),
        html.Hr(),
        html.Pre(pp.pformat(tenv.attr.compile.stdout_parsed), className="pre-wrap")
    ])

def render_error_categories():
    rows = []
    for error_category, error_ct in error_counts.items():
        rows.append( html.Tr( [html.Td(error_category), html.Td(error_ct), html.Td(dcc.Link("*", href=f"/view_random/{error_category}"))] ) )

    table = html.Table( [html.Tr([html.Th("Category"), html.Th("Count"), html.Th("View Random") ])] + rows, className="table")

##### inactive server code

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