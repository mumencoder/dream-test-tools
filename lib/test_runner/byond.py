
import asyncio, time
import Byond, Shared
import common, test_runner

async def do_test(config):
    await compile(config)
    await run(config)

async def compile(config):
    compile_log = config['test.base_dir'] / f"compile.txt"
    with open(compile_log, "w") as log:
        config['process.stdout'] = log
        config['process.stderr'] = log
        process = await Byond.Install.compile(config, config['test.dm_file_path'])
        await asyncio.wait_for(process.wait(), timeout=5.0)
        with open(config['test.base_dir'] / f"compile.returncode.txt", "w") as f_rt:
            f_rt.write(str(process.returncode))

    await config.send_event('test.compile.byond.result', config, process)

async def run(config):
    run_log = config['test.base_dir'] / f"run.txt"
    with open(run_log, "w") as log:
        config['process.stdout'] = log
        config['process.stderr'] = log
        config['process.env'] = {'tag':Shared.Random.generate_string(8)}
        config['process.start_time'] = time.time()
        process = await Byond.Install.run(config, Byond.Install.get_bytecode_file(config['test.dm_file_path']), args={'trusted':True} )
        await common.wait_run_complete(config, process, config['test.base_dir'] / f"fin.out")
        with open(config['test.base_dir'] / f"run.returncode.txt", "w") as f_rt:
            f_rt.write(str(process.returncode))
    await config.send_event('test.run.byond.result', config, process)
