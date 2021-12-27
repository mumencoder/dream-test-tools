
import sys, os
import asyncio, glob, shutil
import Byond, SS13, ClopenDream
from DTT import App

class Main(App):
    async def run(self):
        config = self.config
        Byond.Install.set_current(config, self.config['byond.version'])
        ClopenDream.Install.set_current(config, self.config['clopendream.build.id'])

        async for config in SS13.Repos.iter_community_repos(config):
            if config['ss13.repo_info']['name'] not in self.config['ss13.repo_ids']:
                continue
            SS13.Install.find_dme(config)
            config['clopendream.output.id'] = f"""ss13repo-{config['ss13.repo_info']['name']}"""
            config['clopendream.output.base_dir'] = config['clopendream.dirs.output'] / config['clopendream.output.id']

            await Byond.Install.generate_empty_code_tree(config, config['clopendream.output.base_dir'])
            Byond.Install.prepare_code_tree(config, config['clopendream.output.base_dir'] / 'codetree')
            await Byond.Install.generate_code_tree(config, config['ss13.dme_file'], recompile=False)
            #Byond.Install.prepare_obj_tree(config, config['clopendream.output.base_dir'] / 'objtree')
            #await Byond.Install.generate_obj_tree(config, config['ss13.dme_file'], recompile=True)

            for dir_name in glob.glob(str(config['clopendream.output.base_dir'] / 'mismatch-*')):
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)

            process = await ClopenDream.Install.compare(config)
            await asyncio.wait_for(process.wait(), timeout=None)

asyncio.run( Main().run() )
