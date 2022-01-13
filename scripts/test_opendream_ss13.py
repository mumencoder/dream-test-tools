
import asyncio
import SS13, OpenDream

from DTT import App

class Main(App):
    async def run(self):
        OpenDream.Install.set_current(self.config, self.config['opendream.install.id'])
        async for config in SS13.Repos.iter_community_repos(self.config):
            if config['ss13.repo_info']['name'] not in self.config['ss13.repo_ids']:
                continue

            SS13.Install.find_dme(config)
            process = await OpenDream.Install.compile(config, config['ss13.dme_file'])
            await asyncio.wait_for(process.wait(), timeout=None)
        
main = Main()
asyncio.run( main.run() )