
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

import time

class Main(App):
    async def run(self):
        env = self.env.branch()
        Byond.Install.load(env, 'default')
        env.attr.test.prefix = "test.byond"
        env.attr.test.runner = test_runner.byond.do_test
        await self.run_tests(env)

        OpenDream.Install.load( env, 'main' )
        env.attr.test.prefix = "test.opendream"
        env.attr.test.runner = test_runner.opendream.do_test
        await self.run_tests(env)

        self.running = False
        os.system('stty sane')

main = Main()
asyncio.run( main.start() )