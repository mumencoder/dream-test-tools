
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def clopen_source(self, env):
        await ClopenDream.Source.ensure(env)
        await Shared.Git.Repo.init_all_submodules(env)



        await Shared.Workflow.run_all(self.env)
        self.running = False
        await self.update_report()

main = Main()
asyncio.run( main.start() )