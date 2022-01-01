
import asyncio
import Byond, Shared

async def compile(config):
    config = config.branch('test_byond')

    compile_log = config['test.base_dir'] / "byond.compile.txt"
    with open(compile_log, "w") as log:
        config2 = config.branch('compile')
        config2['process.stdout'] = log
        config2['process.stderr'] = log
        process = await Byond.Install.compile(config2, config['test.dm_file_path'])
        await asyncio.wait_for(process.wait(), timeout=5.0)
    await config2.send_event('test.compile.byond.result', config, process)

async def run(config):
    config['process.env'] = {'tag':Shared.Random.generate_string(8)}
    process = await Byond.Install.run(config, Byond.Install.get_bytecode_file(config['test.dm_file_path']), args={'trusted':True} )
    try:
        await asyncio.wait_for(process.wait(), timeout=5.0)
    except asyncio.exceptions.TimeoutError:
        process.kill()