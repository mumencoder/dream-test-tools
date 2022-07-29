
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    async def prepare_tasks(self):
        self.init_top()
        Shared.Task.link( self.env.attr.scheduler.top_task, Shared.Task( self.env, self.ss13_task, ptags={'action':'ss13_task'} ) )

    @staticmethod
    async def ss13_task(penv, senv):
        for name, source in senv.attr.ss13.sources.items():
            ssenv = senv.branch()
            if source['type'] == 'repo':
                ssenv.attr.ss13.base_dir = ssenv.attr.ss13.dirs.installs / name
                ssenv.attr.git.repo.clone_depth = 2
                ssenv.attr.git.repo.local_dir = ssenv.attr.ss13.base_dir
                ssenv.attr.git.repo.url = source['url']
                await Shared.Git.Repo.ensure(ssenv)
            ssenv.attr.build.dir = ssenv.attr.opendream.dirs.installs / 'local.preproc'
            SS13.Install.find_dme( ssenv )
            ssenv.attr.compilation.dm_file_path = ssenv.attr.ss13.dme_file
            ssenv.attr.compilation.args = {'flags':['experimental-preproc']}
            if ssenv.attr.compilation.dm_file_path:
                await OpenDream.Compilation.compile( ssenv )
            
    async def run(self):
        await self.prepare_tasks()
        await Shared.Scheduler.run( self.env )

main = Main()
asyncio.run( main.start() )