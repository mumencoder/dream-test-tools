
import sys
import asyncio
import Byond, SS13, ClopenDream, test_runner
from DTT import App

class Main(App):
    async def run(self):
        config = self.config
        Byond.Install.set_current(config, self.config['byond.install.id'])
        ClopenDream.Install.set_current(config, self.config['clopendream.install.id'])

        async for config in SS13.Repos.iter_community_repos(config):
            if config['ss13.repo_info']['name'] not in self.config['ss13.repo_ids']:
                continue
            SS13.Install.find_dme(config)
            config['clopendream.output.id'] = f"""ss13repo-{config['ss13.repo_info']['name']}"""
            config['clopendream.output.base_dir'] = config['clopendream.dirs.output'] / config['clopendream.output.id']
            config['clopendream.input_dm'] = config['ss13.dme_file']
            test_runner.clopendream.compile(config)

asyncio.run( Main().run() )