
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    async def run_tasks(self):
        await self.init_top()

    async def run(self):
        await self.run_tasks()

main = Main()
asyncio.run( main.start() )