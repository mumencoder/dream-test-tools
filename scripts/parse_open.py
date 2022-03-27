
import asyncio, time, os, sys
import shutil
import Byond, OpenDream, ClopenDream, SS13, Shared

from DTT import App
import test_runner

class Main(App):
    async def run_opendream(self, ssenv):
        ssenv.attr.git.repo.local_dir = ssenv.attr.ss13.base_dir
        await Shared.Git.Repo.command(ssenv, 'git clean -fdx')

        ssenv.attr.opendream.compilation.dm_file = ssenv.attr.ss13.dme_file
        await self.parse_opendream_ss13(ssenv, 'ClopenDream-compat')

    async def run(self):
        oenv = self.env.branch()

        OpenDream.Install.load(oenv, 'ClopenDream-compat')
        oenv.attr.opendream.compilation.args = {"flags":['experimental-preproc', 'dump-ast']}

        for tenv in test_runner.list_all_tests(oenv, self.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( tenv )
            test_runner.Curated.prepare_test( tenv )
            test_runner.generate_test( tenv )

            Shared.Workflow.open(tenv, f"opendream.test.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, test_runner.opendream.compile(tenv) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        for ssenv in self.iter_ss13_tests(oenv):
            Shared.Workflow.open(ssenv, f"ss13.compile.{ssenv.attr.ss13.repo_name}")
            Shared.Workflow.set_task(ssenv, self.run_opendream(ssenv) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

main = Main()
asyncio.run( main.start() )