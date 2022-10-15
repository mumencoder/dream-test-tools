
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    def byond_env(self, env):
        benv = env.branch()
        benv.attr.install.version = '514.1566'
        benv.attr.install.id = benv.attr.install.version
        DTT.tasks.Byond.load_install(benv)
        return benv

    def wix_github_env(self, env):
        ghenv = env.branch()
        ghenv.attr.github.repo.owner = 'wixoaGit'
        ghenv.attr.github.repo.name = 'OpenDream'
        ghenv.attr.github.repo.tag = ''
        ghenv.attr.github.repo.dir = env.attr.opendream.dirs.repos
        return ghenv

    def local_opendream_env(self, env):
        locenv = env.branch()
        locenv.attr.build.id = f"local.{self.cmd_args['id']}"
        locenv.attr.build.dir = Shared.Path( self.cmd_args["dir"] )
        return locenv

    async def run_local(self):
        benv = self.byond_env(self.env)
        ghenv = self.wix_github_env(self.env)
        locenv = self.local_opendream_env(self.env)

        await DTT.tasks.Byond.ensure_install(benv)
        return
        
    def clean_data(self):
        import shutil
        shutil.rmtree( self.env.attr.dirs.root )

    async def run(self):
        self.env.attr.config.redo_tests = []
        Shared.Dotnet.reset()
        await self.run_tasks()

    def process_args(self):
        from optparse import OptionParser
        parser = OptionParser()
        self.cmd_args = {}
        if sys.argv[1] == "":
            pass
        elif sys.argv[1] == "run_local":
            self.run_tasks = self.run_local
            self.cmd_args["id"] = sys.argv[2]
            self.cmd_args["dir"] = sys.argv[3]
        elif sys.argv[1] == "clean_data":
            self.run_tasks = self.clean_data
        else:
            raise Exception("invalid command", sys.argv[1])

main = Main()
main.process_args()
asyncio.run( main.start() )