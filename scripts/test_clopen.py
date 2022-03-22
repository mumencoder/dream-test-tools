
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        clenv = self.env.branch()
        self.build_clopendream(clenv, 'currentdev')

        self.prepare_empty_clopendream(clenv)

        for tenv in test_runner.list_all_tests(clenv, self.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( tenv )
            test_runner.Curated.prepare_test( tenv )
            test_runner.generate_test( tenv )

            Byond.Install.load(tenv, 'default')
            Shared.Workflow.open(tenv, f"test.byond.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, test_runner.byond.codetree(tenv) )

        await Shared.Workflow.run_all(self.env)

        for tenv in test_runner.list_all_tests(clenv, self.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( tenv )

            tenv.attr.clopendream.install.working_dir = tenv.attr.test.base_dir
            tenv.attr.byond.codetree = tenv.attr.test.base_dir / 'test.codetree'
            Shared.Workflow.open(tenv, f"test.clopendream.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, ClopenDream.Install.parse(tenv) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

main = Main()
asyncio.run( main.start() )