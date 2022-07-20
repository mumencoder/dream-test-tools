
import asyncio, time, os, sys, shutil
import collections

import Shared
import DTT
from DTT.base import *

class Main(DTT.App):
    def monitor_target(env):
        DTT.tasks.Monitoring.register_metrics(env)

    def byond_env(env):
        benv = env.branch()
        benv.attr.byond.install.version = '514.1566'
        return benv

    def wix_github_env(env):
        ghenv = env.branch()
        ghenv.attr.github.owner = 'wixoaGit'
        ghenv.attr.github.repo = 'OpenDream'
        ghenv.attr.github.tag = ''
        ghenv.attr.github.repo.dir = env.attr.opendream.dirs.repos
        return ghenv

    def run_local(self):
        benv = self.byond_env(self.env)
        ghenv = self.wix_github_env(self.env)

        locenv = self.env.branch()
        locenv.attr.build.id = f"local.{self.cmd_args['id']}"
        locenv.attr.build.dir = Shared.Path( self.cmd_args["dir"] )

        targets = [
            self.byond_target(benv),
            DTT.tasks.Github.Targets.update_pull_requests(ghenv),
            self.commit_history_target(ghenv),
        ]

        base_commit = Shared.Git.search_base_commit( locenv, locenv.attr.git.commit, self.pull_request_target(ghenv).commits() )
        baseenv = self.github_target(ghenv).get_install(base_commit)

        comp_env = self.env.branch()
        comp_env.attr.compare.ref = self.byond_target(benv).get_install()
        comp_env.attr.compare.prev = baseenv
        comp_env.attr.compare.next = locenv

        self.compare_report_target(comp_env)

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
            self.cmd_args["id"] = sys.argv[2]
            self.cmd_args["dir"] = sys.argv[3]
        elif sys.argv[1] == "clean_data":
            self.run_tasks = self.clean_data
        else:
            raise Exception("invalid command", sys.argv[1])

main = Main()
main.process_args()
asyncio.run( main.start() )