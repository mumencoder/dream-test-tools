
import asyncio
import Shared, OpenDream

async def compile(config):
    config = config.branch('test_open')
    with open(config['test.base_dir'] / 'opendream.compile.txt', "w") as o:
        config['process.stdout'] = o
        config['process.stderr'] = o
        process = await OpenDream.Install.compile(config, config['test.dm_file_path'])
        await asyncio.wait_for(process.wait(), timeout=5.0)
    await config.send_event('test.compile.opendream.result', config, process)

async def run(config):
    config = config.branch('test_run')
    with open(config['test.base_dir'] / 'opendream.run.txt', "w") as o:
        config['process.stdout'] = o
        config['process.stderr'] = o
        process = await OpenDream.Install.run(config, OpenDream.Install.get_bytecode_file(config['test.dm_file_path']))
        await asyncio.wait_for(process.wait(), timeout=None)