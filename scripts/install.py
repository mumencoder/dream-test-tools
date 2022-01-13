
import sys, asyncio
from DTT import App

class Main(App):
    async def run(self):
        await self.install(sys.argv[1], sys.argv[2])

asyncio.run( Main().run() )