import sys
import asyncio
import OpenDream

from DTT import App

class Main(App):
    async def run(self):
        await self.prepare_opendream_local(sys.argv[1], sys.argv[2])
        await OpenDream.Builder.build(self.config)

asyncio.run( Main().run() )