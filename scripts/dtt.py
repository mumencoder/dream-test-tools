
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    def run_common(self):
        self.env.attr.byond.install.version = '514.1566'
        self.init_top()
        self.env.attr.named_tasks = {}
        DTT.tasks.Monitoring.register_metrics(self.env)

    def run_byond(self, env):
        env = env.branch()
        tasks = [
            DTT.Byond.Setup.install(env),
            DTT.Byond.Setup.tests(env)
        ]
        return Shared.Task.bounded_tasks( *tasks )

    def run_opendream(self, env):
        env = env.branch()
        DTT.tasks.OpenDream.Setup.metadata(env)

        tasks = [
            DTT.tasks.OpenDream.Setup.github(env),
            DTT.tasks.OpenDream.Setup.update_pull_requests(env),
            DTT.tasks.OpenDream.Setup.update_commit_history(env),
            DTT.tasks.OpenDream.Setup.shared_repos(env),
            DTT.tasks.OpenDream.Setup.process_pull_requests(env),
            DTT.tasks.OpenDream.Setup.process_commit_history(env),
        ]
        return Shared.Task.bounded_tasks( *tasks )

    def run_wix_main(self):
        env = self.env.branch()
        async def set_senv(penv, senv):
            senv.attr.github.owner = 'wixoaGit'
            senv.attr.github.repo = 'OpenDream'
            senv.attr.github.tag = ''
        #Shared.Task.chain( env.attr.scheduler.top_task, self.run_byond(env) )
        Shared.Task.chain( env.attr.scheduler.top_task,
            Shared.Task(env, set_senv, ptags={'action':'set_senv'}, unique=False),
            self.run_opendream(env)
        )

    def clean_data(self):
        import shutil
        shutil.rmtree( self.env.attr.dirs.root )

    async def run(self):
        self.env.attr.config.redo_tests = []
        Shared.Dotnet.reset()
        self.run_common()
        self.run_tasks()
        await Shared.Scheduler.run( self.env )

    def process_args(self):
        from optparse import OptionParser
        parser = OptionParser()
        self.cmd_args = {}
        if sys.argv[1] == "":
            pass
        elif sys.argv[1] == "run_wix_main":
            self.run_tasks = self.run_wix_main
        elif sys.argv[1] == "run_local":
            self.run_tasks = self.run_local
            self.cmd_args["dir"] = sys.argv[2]
        elif sys.argv[1] == "clean_data":
            self.run_tasks = self.clean_data
        else:
            raise Exception("invalid command", sys.argv[1])

main = Main()
main.process_args()
asyncio.run( main.start() )