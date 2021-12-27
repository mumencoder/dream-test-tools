
import asyncio
import OpenDream

from DTT import App

class Main(App):
    async def run(self):
        await self.prepare_opendream_repo(self.config['opendream.build.id'])
        await OpenDream.Builder.build(self.config)

asyncio.run( Main().run() )