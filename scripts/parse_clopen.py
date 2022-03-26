
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared, SS13

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        clenv = self.env.branch()

        for tenv in test_runner.list_all_tests(clenv, self.env.attr.tests.dirs.dm_files):
            ClopenDream.Install.load(tenv, 'currentdev')
            test_runner.Curated.load_test( tenv )
            test_runner.Curated.prepare_test( tenv )
            test_runner.generate_test( tenv )

            tenv.attr.byond.compilation.file_path = tenv.attr.test.dm_file_path
            tenv.attr.clopendream.install.working_dir = tenv.attr.test.base_dir

            Shared.Workflow.open(tenv, f"clopendream.test.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, self.parse_clopendream_test(tenv, 'currentdev') )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        for repo_name, repo in self.env.attr.ss13.sources.items():
            ssenv = clenv.branch()

            ssenv.attr.ss13.repo_name = repo_name
            ssenv.attr.ss13.base_dir = self.env.attr.ss13.dirs.installs / repo_name
            SS13.Install.find_dme( ssenv )
            if ssenv.attr.ss13.dme_file is None:
                continue

            ssenv.attr.byond.compilation.file_path = ssenv.attr.ss13.dme_file

            Shared.Workflow.open(ssenv, f"clopendream.ss13.{repo_name}")
            Shared.Workflow.set_task(ssenv, self.parse_clopendream_ss13(ssenv, 'currentdev') )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

main = Main()
asyncio.run( main.start() )