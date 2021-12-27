
import asyncio 
import traceback
import Shared, SS13
import dream_collider

from DTT import App

class Main(App):
    async def update(self):
        async for config in SS13.Repos.iter_community_repos(self.config):
            try:
                repo_info = config['ss13.repo_info']
                print(f"==================================updating {repo_info['name']}")

                self.config = self.config.branch().merge( config )
                await self.prepare_ss13_repo( repo_info )
                self.config = self.config.pop()
            except:
                print(traceback.print_exc())

main = Main()
asyncio.run( main.update() )