

import datetime as dt
import asyncio, time, os
import git

import Byond, OpenDream, ClopenDream, Shared
from DTT import App
import test_runner

class Main(App):
    async def run(self):
        oenv = self.env.branch()
        OpenDream.Source.load(oenv, 'main')
        repo = git.Repo( oenv.attr.opendream.source.dir )
        oenv.attr.git.repo = repo
        commit = repo.commit('origin/HEAD')
        commits = Shared.Git.Repo.commit_history(commit, depth=32)

        for c in commits:
            build_env = self.env.branch()
            build_env.attr.git.repo.remote = 'origin'
            build_env.attr.git.repo.remote_ref = str(c)
            OpenDream.Install.load(build_env, f'github.wixoaGit.{str(c)}')
            Shared.Workflow.open(build_env, f"opendream.build.{str(c)}")
            Shared.Workflow.set_task(build_env, self.build_opendream(build_env))

            await Shared.Workflow.run_all(self.env)
            await self.update_report()

            build_env.attr.test.prefix = "test.opendream"
            build_env.attr.test.runner = test_runner.opendream.do_test
            await self.run_tests(build_env)

        self.running = False
        os.system('stty sane')


main = Main()
asyncio.run( main.start() )