
import os
import asyncio, time
import sys
import Shared

class Process(object):
    @staticmethod
    async def split_stream_filename(prefix, postfix):
        out = f"{prefix}out{postfix}"
        err = f"{prefix}err{postfix}"
        return out, err
    
    @staticmethod
    @Shared.wf_tag('process')
    async def shell(env):
        env = env.branch()
        try:
            await env.attr.resources.process.acquire(env)
            
            process = env.prefix('.process')
            shell = env.prefix('.shell')

            if process.log_mode == "auto":
                process.auto_log = {"path": env.attr.dirs.ramdisc / "auto_process_logs" / Shared.Random.generate_string(16)}
                process.auto_log["f"] = open(process.auto_log["path"], "w")
                process.stdout = process.stderr = process.auto_log["f"]

            with Shared.Workflow.status(env, "launching process"):
                shell_env = dict(os.environ)
                shell_env.update( env.get_dict('.process.env') )

                if env.attr_exists( ".shell.dir" ):
                    pushd = shell.dir
                else:
                    pushd = os.getcwd()

                with Shared.folder.Push( pushd ):
                    if env.attr_exists('.process.p'):
                        raise Exception("process already exists") 
                    env.attr.wf.log.append( {'type':'shell', 'env':env} )
                    process.start_time = time.time()
                    process.p = await asyncio.create_subprocess_shell(env.attr.shell.command, stdout=process.stdout, stderr=process.stderr, env=shell_env)
                    env.attr.wf.status[-1] = "process running"

                    if env.event_defined('process.wait'):
                        await env.send_event("process.wait", env)
                    else:
                        await asyncio.wait_for(process.p.wait(), timeout=None)

                if process.log_mode == "auto":
                    process.auto_log["f"].close()

                await env.send_event("process.complete", env)
        finally:
            env.attr.resources.process.release(env)