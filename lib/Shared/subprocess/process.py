
import os
import asyncio, time
import sys
import Shared

class Process(object):
    ### Inputs
    # .shell.dir - sets current working directory for process
    # .shell.env - environment variables to launch process with
    # .process.stdout - a stream to log process stdout
    # .process.stderr - a stream to log process stderr, if missing will use same stream as .process.stdout
    ### Outputs
    # .process.instance
    # .shell.start_time
    # .shell.finish_time
    ### Notes
    # This can only be called in an environment once, multiple runs with the same inputs must use a freshly branched environment
    @staticmethod
    async def shell(env):
        env = env.branch()
        process = env.prefix('.process')
        shell = env.prefix('.shell')

        if not env.attr_exists('.shell.env'):
            raise Exception(".shell.env not set")
        if not env.attr_exists('.process.stdout'):
            raise Exception(".process.stdout not set")
        if not env.attr_exists( ".process.stderr" ):
            process.stderr = process.stdout

        if env.attr_exists('.process.instance'):
            raise Exception(".process.instance already exists") 

        await env.send_event("process.initialize", env)
        try:
            if env.attr_exists( ".shell.dir" ):
                pushd = shell.dir
            else:
                pushd = os.getcwd()

            with Shared.folder.Push( pushd ):
                await env.send_event("process.starting", env)
                process.start_time = time.time()
                process.instance = await asyncio.create_subprocess_shell(shell.command, stdout=process.stdout, stderr=process.stderr, env=shell.env)
                await env.send_event("process.started", env)

                if env.event_defined('process.wait'):
                    await env.send_event("process.wait", env)
                else:
                    await asyncio.wait_for(process.instance.wait(), timeout=None)

                process.finish_time = time.time()
                await env.send_event("process.finished", env)
        finally:
            await env.send_event("process.cleanup")
