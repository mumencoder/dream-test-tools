
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
    @Shared.Workflow.Decorators.status('Process.shell')
    async def shell(env):
        env = env.branch()
        res = await env.attr.resources.process.acquire()
        try:
            process = env.prefix('.process')
            shell = env.prefix('.shell')

            if process.log_mode == "auto":
                process.log_path = process.auto_log_path / Shared.Random.generate_string(16)
                
            if type(process.log_path) in [str, Shared.filesystem.folder.Path]:
                process.stdout = process.stderr = Shared.File.open(process.log_path, "w")

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
                    Shared.Workflow.log_shell( env )
                    process.start_time = time.time()
                    process.p = await asyncio.create_subprocess_shell(env.attr.shell.command, stdout=process.stdout, stderr=process.stderr, env=shell_env)
                    Shared.Workflow.update_status( "process running" )

                    if env.event_defined('process.wait'):
                        await env.send_event("process.wait", env)
                    else:
                        await asyncio.wait_for(process.p.wait(), timeout=None)

                if type(process.log_path) in [str, Shared.filesystem.folder.Path]:
                    process.stdout.close()

                await env.send_event("process.complete", env)
        finally:
            env.attr.resources.process.release(res)