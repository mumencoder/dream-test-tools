
import os

import asyncio

async def wait_run_complete(env):
    process = env.attr.process.p
    fin_path = env.attr.test.base_dir / 'fin.out'
    while process.returncode is None:
        if os.path.exists(fin_path):
            if os.stat(fin_path).st_mtime > env.attr.process.start_time:
                try:
                    process.kill()
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.exceptions.TimeoutError:
                    pass
        try:
            await asyncio.wait_for(process.wait(), timeout=0.10)
        except asyncio.exceptions.TimeoutError:
            pass
