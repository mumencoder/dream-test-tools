
import fastapi
import fastapi.security.api_key as apiseckey

from common import *

app = fastapi.FastAPI()
root_env = base_env()

redis_conn = redis.Redis(host="redis")
work_queue = rq.Queue(connection=redis_conn)
job_index = {}

@app.get("/action/{action_name}/{resource_name}")
async def action(action_name : str, resource_name : str, request : fastapi.Request):
    env = root_env.branch()
    env.attr.resource_metadata_dir = env.attr.metadata_dir / 'resources' / resource_name
    rtype = root_env.attr.config_file['resources'][resource_name]['type']
    if rtype == "byond_install":
        install_id = resource_name
        load_byond_install(env, install_id)
    if rtype == 'opendream_repo':
        install_id = resource_name
        load_opendream_install(env, install_id)
    if rtype == 'churn':
        churn_id = resource_name
        load_churn(env, churn_id)
    if rtype == 'dream_repo':
        repo_id = resource_name
        load_dream_repo(env, repo_id)
    if action_name == "download":
        env.attr.install.save_path = env.attr.tmp_dir / 'byond.zip'
        Shared.Process.pipe_stdout(env)
        await DMShared.Byond.Download.linux(env)
        await DMShared.Byond.Install.from_zip(env)
        put_file( env.attr.resource_metadata_dir / 'action_download_stdout', env.attr.process.stdout.getvalue() )
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
        Shared.Process.pipe_stdout(env)
        await Shared.Git.Repo.clone(env)
        put_file( env.attr.resource_metadata_dir / 'action_clone_stdout', env.attr.process.stdout.getvalue() )
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
        metadata = maybe_from_pickle( get_file(env.attr.resource_metadata_dir / 'build.pkcl'), default_value={} )
        metadata['last_build_commit'] = status['branch.oid']
        put_file( env.attr.resource_metadata_dir / 'build.pkcl', pickle.dumps(metadata) )
    if action_name == "dream_build":
        env.attr.compilation.root_dir = env.attr.git.repo.dir
        DMShared.SS13.Compilation.find_dme(env)

        benv = env.branch()
        load_byond_install(benv, "byond_main")
        await DMShared.Byond.Compilation.managed_compile(benv)
        print( benv.attr.compile.stdout.getvalue() )

        oenv = env.branch()
        load_opendream_install(oenv, "opendream_main")
        await DMShared.OpenDream.Compilation.managed_compile(oenv)
        print( oenv.attr.compile.stdout.getvalue() )

    if action_name == 'submodule_init':
        await Shared.Git.Repo.init_all_submodules(env)

@app.get("/installs/list")
async def installs(request : fastapi.Request):
    env = root_env.branch()
    def is_install_type(rtype):
        return rtype in ["byond_install", "opendream_repo", "dream_repo"]
    
    resources = {}
    for resource_name, resource in root_env.attr.config_file['resources'].items():
        if not is_install_type(resource['type']):
            continue

        result = {}
        result["state"] = await globals()[f"status_{resource['type']}"](env, resource_name)
        result["resource"] = resource
        if os.path.exists( env.attr.metadata_dir / 'resources' / resource_name ):
            result["metadata"] = os.listdir( env.attr.metadata_dir / 'resources' / resource_name )
        resources[resource_name] = result

    return resources

@app.get("/installs/view_metadata/{resource_name}/{filename}")
async def installs_view_metadata(resource_name : str, filename : str, request : fastapi.Request):
    env = root_env.branch()
    file_path = env.attr.metadata_dir / 'resources' / resource_name / filename
    if os.path.exists( file_path ):
        with open( file_path, "rb") as f:
            return f.read().decode('ascii')


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