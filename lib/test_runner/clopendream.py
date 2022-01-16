
import asyncio, sys, os
import glob, shutil
import common, test_runner
import Byond, ClopenDream

async def prep_tree(config):
    await Byond.Install.generate_empty_code_tree(config, config['clopendream.output.base_dir'])
    Byond.Install.prepare_code_tree(config, config['clopendream.output.base_dir'] / 'codetree')
    config['byond.codetree.recompile'] = True

    config['process.stdout'] = open(config['byond.codetree.out'], "wb")
    config['process.stderr'] = open(config['byond.codetree.err'], "wb")
    await Byond.Install.generate_code_tree(config, config['clopendream.input_dm'] )
    config['process.stdout'].close()
    config['process.stderr'].close()

async def do_test(config):
    final_text = test_runner.TestWrapper(config, config['test.text']).wrapped_test(config)
    await test_runner.write_test(config, final_text)

    config['clopendream.input_dm'] = config['test.dm_file_path']
    config['clopendream.output.base_dir'] = config['test.base_dir']
    await test_runner.clopendream.compare(config)

async def compare(config):
    await prep_tree(config)
    for dir_name in glob.glob(str(config['clopendream.output.base_dir'] / 'mismatch-*')):
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)

    config['process.stdout'] = sys.stdout
    config['process.stderr'] = sys.stderr
    with open(config['test.base_dir'] / f"compare.txt", "w") as o:
        config['process.stdout'] = o
        config['process.stderr'] = o
        process = await ClopenDream.Install.compare(config)
        await asyncio.wait_for(process.wait(), timeout=None)
        with open(config['test.base_dir'] / f"compare.returncode.txt", "w") as f_rt:
            f_rt.write(str(process.returncode))


async def compile(config):
    await prep_tree(config)
    process = await ClopenDream.Install.compile(config)
    await asyncio.wait_for(process.wait(), timeout=None)

async def obj_tree(config):
    Byond.Install.prepare_obj_tree(config, config['clopendream.output.base_dir'] / 'objtree')
    await Byond.Install.generate_obj_tree(config, config['clopendream.input_dm'], recompile=True)
