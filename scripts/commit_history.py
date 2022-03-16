

import datetime as dt
import asyncio, time, os
import git

import Byond, OpenDream, ClopenDream, Shared
from DTT import App
import test_runner

class Main(App):
    async def run(self):
        oenv = self.env

        oenv.attr.opendream.sources['default_full_history'] = oenv.attr.opendream.sources['default']
        oenv.attr.install.platform = "opendream"
        oenv.attr.git.repo.clone_depth = 512
        OpenDream.Source.load(oenv, 'default_full_history')
        oenv.attr.opendream.install.dir = oenv.attr.opendream.source.dir

        Shared.Workflow.open(oenv, f"opendream.full")
        Shared.Workflow.set_task(oenv, OpenDream.Source.ensure(oenv) )
        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        repo = git.Repo( oenv.attr.opendream.source.dir )
        repo.remote('origin').pull(depth=512)

        commit = repo.commit('HEAD~0')
        oenv.attr.git.repo = repo

        commits = Shared.Git.Repo.commit_history(commit, depth=16)
        for c in commits:
            repo.head.reference = repo.head.reference = c
            repo.head.reset(index=True, working_tree=True)

            build_env = oenv.branch()
            build_env.attr.install.id = f'github.main.{str(c)}'
            Shared.Workflow.open(build_env, f"opendream.build.{str(c)}")
            Shared.Workflow.set_task(build_env, OpenDream.Builder.build(build_env) )

            await Shared.Workflow.run_all(self.env)
            await self.update_report()

            for tenv in test_runner.list_all_tests(build_env, self.env.attr.tests.dirs.dm_files):
                test_runner.Curated.load_test( tenv )
                test_runner.Curated.prepare_test( tenv )
                test_runner.generate_test( tenv )
                Shared.Workflow.open(tenv, f"test.opendream.{tenv.attr.test.id}.{str(c)}")
                Shared.Workflow.set_task(tenv, test_runner.opendream.do_test(tenv) )

            await Shared.Workflow.run_all(self.env)
            await self.update_report()

        self.running = False
        os.system('stty sane')


main = Main()
asyncio.run( main.start() )