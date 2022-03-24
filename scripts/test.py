
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        env = self.env.branch()
        await self.update_mains(env)

main = Main()
asyncio.run( main.start() )