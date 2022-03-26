
import asyncio, time, os, sys
import shutil
import Byond, OpenDream, ClopenDream, SS13, Shared

from DTT import App
import test_runner

class Main(App):
    async def parse_ast(self, ssenv):
        await OpenDream.Compilation.compile(ssenv)
        self.ss13_test(ssenv)
        shutil.move( ssenv.attr.ss13.base_dir / "ast.json", ssenv.attr.test.base_dir / "ast.json")

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

        for repo_name, repo in self.env.attr.ss13.sources.items():
            ssenv = oenv.branch()

            ssenv.attr.ss13.repo_name = repo_name
            ssenv.attr.ss13.base_dir = self.env.attr.ss13.dirs.installs / repo_name
            SS13.Install.find_dme( ssenv )
            if ssenv.attr.ss13.dme_file is None:
                continue

            ssenv.attr.opendream.compilation.dm_file = ssenv.attr.ss13.dme_file
            Shared.Workflow.open(ssenv, f"ss13.compile.{repo_name}")
            Shared.Workflow.set_task(ssenv, self.parse_ast(ssenv))

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

main = Main()
asyncio.run( main.start() )