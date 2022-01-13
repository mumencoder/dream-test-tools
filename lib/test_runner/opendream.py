
import asyncio, time
import Shared, OpenDream
import common, test_runner

async def do_test(config):
    config['test.platform'] = f"opendream.{config['opendream.install.id']}"
    final_text = test_runner.TestWrapper(config, config['test.text']).wrapped_test(config)
    await test_runner.write_test(config, final_text)

    await compile(config)
    await run(config)

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
        config['process.start_time'] = time.time()
        process = await OpenDream.Install.run(config, OpenDream.Install.get_bytecode_file(config['test.dm_file_path']))
        await common.wait_run_complete(config, process, config['test.base_dir'])
    await config.send_event('test.run.opendream.result', config, process)
