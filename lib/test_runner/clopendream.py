
import asyncio
import glob, os, shutil
import Byond, ClopenDream

async def prep_tree(config):
    await Byond.Install.generate_empty_code_tree(config, config['clopendream.output.base_dir'])
    Byond.Install.prepare_code_tree(config, config['clopendream.output.base_dir'] / 'codetree')
    await Byond.Install.generate_code_tree(config, config['test.dm_file_path'] , recompile=False)

async def compare(config):
    await prep_tree(config)
    for dir_name in glob.glob(str(config['clopendream.output.base_dir'] / 'mismatch-*')):
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)

    config['clopendream.input_dm'] = config['test.dm_file_path']
    process = await ClopenDream.Install.compare(config)
    await asyncio.wait_for(process.wait(), timeout=None)

async def compile(config):
    await prep_tree(config)
    process = await ClopenDream.Install.compile(config)
    await asyncio.wait_for(process.wait(), timeout=None)

async def obj_tree(config):
    Byond.Install.prepare_obj_tree(config, config['clopendream.output.base_dir'] / 'objtree')
    await Byond.Install.generate_obj_tree(config, config['test.dm_file_path'] , recompile=True)
