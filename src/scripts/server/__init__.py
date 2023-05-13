
import fastapi
import fastapi.security.api_key as apiseckey

from common import *

app = fastapi.FastAPI()
root_env = base_env()

redis_conn = redis.Redis(host="redis")
work_queue = rq.Queue(connection=redis_conn)
job_index = {}

class Actions:
    class ByondInstall:
        async def download(env, resource):
            env.attr.install.zip = env.attr.tmp_dir / 'byond.zip'

            Shared.Process.pipe_stdout(env)
            await DMShared.Byond.Download.linux(env)
            put_metadata( resource, 'action_download_stdout', env.attr.process.stdout.getvalue() )

            Shared.Process.pipe_stdout(env)
            await DMShared.Byond.Install.from_zip(env)
            put_metadata( resource, 'action_from_zip_stdout', env.attr.process.stdout.getvalue() )

    class Churn:
        async def clear(env, resource):
            env.attr.churn.config.result_dir.ensure_clean_dir()

        async def start(env, resource):
            job_uuid = (resource['name'], "churn")
            jstat = job_status(job_index, job_uuid)
            if jstat not in ["finished", "failed"]:
                return
            job = rq.job.Job.create(churn_run, [resource['name']], timeout='48h', connection=redis_conn)
            work_queue.enqueue_job(job)
            job_index[(resource['name'], "churn")] = job

async def action_compile_ByondInstall_DMFile(env, install, dmfile):
    env.attr.compilation.root_dir = env.attr.git.repo.dir
    DMShared.SS13.Compilation.find_dme(env)

    benv = env.branch()
    load_byond_install(benv, "byond_main")
    await DMShared.Byond.Compilation.managed_compile(benv)
    print( benv.attr.compile.stdout.getvalue() )

async def action_compile_OpenDreamInstall_DMFile(env, install, dmfile):
    env.attr.compilation.root_dir = env.attr.git.repo.dir
    DMShared.SS13.Compilation.find_dme(env)

    oenv = env.branch()
    load_opendream_install(oenv, "opendream_main")
    await DMShared.OpenDream.Compilation.managed_compile(oenv)
    print( oenv.attr.compile.stdout.getvalue() )

