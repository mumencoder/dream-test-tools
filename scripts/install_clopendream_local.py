import sys
import asyncio
import ClopenDream

from DTT import App

class Main(App):
    async def run(self):
        await self.prepare_clopendream_local(sys.argv[1], sys.argv[2])
        await ClopenDream.Builder.build(self.config)

asyncio.run( Main().run() )