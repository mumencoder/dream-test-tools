
import os
import asyncio, time
import sys
import Shared

class Process(object):
    @staticmethod
    async def shell(config, command):
        stdout = config['process.stdout']
        stderr = config['process.stderr']
        env = dict(os.environ)
        env.update( config.get_dict('process.env') )

        process = await asyncio.create_subprocess_shell(command, stdout=stdout, stderr=stderr, env=env)
        await config.send_event('process.create', process)

        return process