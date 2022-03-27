
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        for tenv in test_runner.list_all_tests(self.env, self.env.attr.tests.dirs.dm_files):
            clenv = tenv.branch()
            ClopenDream.Source.load(clenv, 'currentdev')
            ClopenDream.Install.load(clenv, 'currentdev')

            test_runner.Curated.load_test( clenv )
            clenv.attr.clopendream.run.working_dir = clenv.attr.test.base_dir

            clod_json_path = clenv.attr.test.base_dir / 'clopen_ast.json'
            if not os.path.exists(clod_json_path):
                continue
            clenv.attr.clopendream.run.ast1 = clod_json_path

            oenv = tenv.branch()
            OpenDream.Source.load(oenv, 'ClopenDream-compat')
            OpenDream.Install.load(oenv, 'ClopenDream-compat')
            test_runner.Curated.load_test( oenv )

            od_json_path = oenv.attr.test.base_dir / 'ast.json'
            if not os.path.exists(od_json_path):
                continue
            clenv.attr.clopendream.run.ast2 = od_json_path

            Shared.Workflow.open(clenv, f"clopendream.compare.curated.{clenv.attr.test.id}")
            Shared.Workflow.set_task(clenv, ClopenDream.Install.compare(clenv) )

        for ssenv in self.iter_ss13_tests(self.env):
            clenv = ssenv.branch()
            ClopenDream.Source.load(clenv, 'currentdev')
            ClopenDream.Install.load(clenv, 'currentdev')
            self.load_ss13_test(clenv)

            clenv.attr.clopendream.run.working_dir = clenv.attr.test.base_dir
            clod_json_path = clenv.attr.test.base_dir / 'clopen_ast.json'
            if not os.path.exists(clod_json_path):
                continue
            clenv.attr.clopendream.run.ast1 = clod_json_path

            oenv = ssenv.branch()
            OpenDream.Source.load(oenv, 'ClopenDream-compat')
            OpenDream.Install.load(oenv, 'ClopenDream-compat')
            self.load_ss13_test(oenv)
            od_json_path = oenv.attr.test.base_dir / 'ast.json'
            if not os.path.exists(od_json_path):
                continue
            clenv.attr.clopendream.run.ast2 = od_json_path

            Shared.Workflow.open(clenv, f"clopendream.compare.ss13.{clenv.attr.ss13.repo_name}")
            Shared.Workflow.set_task(clenv, ClopenDream.Install.compare(clenv) )

            await Shared.Workflow.run_all(self.env)
            await self.update_report()

main = Main()
asyncio.run( main.start() )