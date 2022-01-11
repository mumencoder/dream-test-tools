
import os

import asyncio

async def wait_run_complete(config, process, fin_path):
    while process.returncode is None:
        if os.path.exists(fin_path):
            if os.stat(fin_path).st_mtime > config['process.start_time']:
                process.kill()
                await asyncio.wait_for(process.wait(), timeout=2.0)
                continue
        try:
            await asyncio.wait_for(process.wait(), timeout=0.10)
        except asyncio.exceptions.TimeoutError:
            pass