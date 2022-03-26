
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, SS13, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        env = self.env.branch()
        source = env.attr.clopendream.sources.currentdev
        Shared.Workflow.open(env, f"clopendream.{source.id}")
        Shared.Workflow.set_task(env, self.ensure_clopendream(env, source) )
        await Shared.Workflow.run_all(self.env)

        env = self.env.branch()
        await self.update_mains(env)
        await Shared.Workflow.run_all(env)

        self.running = False
        os.system('stty sane')

main = Main()
asyncio.run( main.start() )