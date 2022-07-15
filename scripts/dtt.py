
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

        gh_task = DTT.tasks.OpenDream.Setup.github(env)

        pr_task = DTT.tasks.OpenDream.Setup.update_pull_requests(env)
        Shared.Task.link( gh_task, pr_task )

        ch_task = DTT.tasks.OpenDream.Setup.update_commit_history(env, n=env.attr.history.n)
        Shared.Task.link( gh_task, ch_task )
        Shared.Task.link( pr_task, ch_task, ltype="exec" )
      
        return Shared.TaskBound(gh_task, ch_task)

    def run_wix_main(self):
        env = self.env.branch()
        env.attr.history.n = 16
        async def set_senv(penv, senv):
            senv.attr.github.owner = 'wixoaGit'
            senv.attr.github.repo = 'OpenDream'
            senv.attr.github.tag = ''
        #Shared.Task.chain( env.attr.scheduler.top_task, self.run_byond(env) )
        Shared.Task.chain( env.attr.scheduler.top_task,
            Shared.Task(env, set_senv, ptags={'action':'set_senv'}, unique=False),
            self.run_opendream(env)
        )

    def run_local(self):
        env = self.env.branch()
        env.attr.history.n = 2
        async def set_senv(penv, senv):
            senv.attr.github.owner = 'wixoaGit'
            senv.attr.github.repo = 'OpenDream'
            senv.attr.github.tag = ''
        od_task = self.run_opendream(env)
        Shared.Task.chain( env.attr.scheduler.top_task,
            Shared.Task(env, set_senv, ptags={'action':'set_senv'}, unique=False),
            od_task
        )
        local_task = DTT.tasks.OpenDream.Setup.update_local(env, '', self.cmd_args["dir"] )
        Shared.Task.chain( env.attr.scheduler.top_task, local_task )
        Shared.Task.link( od_task, local_task, ltype="exec")

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