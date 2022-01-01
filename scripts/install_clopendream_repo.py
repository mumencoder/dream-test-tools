
import asyncio
import ClopenDream

from DTT import App

class Main(App):
    async def run(self):
        await self.prepare_clopendream_repo(self.config['clopendream.build.id'])
        await ClopenDream.Builder.build(self.config)

asyncio.run( Main().run() )