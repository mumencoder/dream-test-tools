
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        clenv = self.env.branch()
        self.build_clopendream(clenv, 'currentdev')

        for tenv in test_runner.list_all_tests(env, self.env.attr.tests.dirs.dm_files):
            clenv = tenv.branch()
            ClopenDream.Source.load(clenv, 'currentdev')
            test_runner.Curated.load_test( clenv )

            clod_json_path = clenv.attr.test.base_dir / 'clopen_ast.json'
            if not os.path.exists(clod_json_path):
                continue
            clenv.attr.clopendream.ast1 = clod_json_path
            clenv.attr.clopendream.install.working_dir = clenv.attr.test.base_dir
            clenv.attr.clopendream.install.dir = clenv.attr.clopendream.source.dir

            oenv = tenv.branch()
            OpenDream.Source.load(oenv, 'clopendream')
            test_runner.Curated.load_test( oenv )

            od_json_path = oenv.attr.test.base_dir / 'ast.json'
            if not os.path.exists(od_json_path):
                continue
            clenv.attr.clopendream.ast2 = od_json_path

            Shared.Workflow.open(clenv, f"clopendream.compare.{clenv.attr.test.id}")
            Shared.Workflow.set_task(clenv, ClopenDream.Install.compare(clenv, oenv) )


        await Shared.Workflow.run_all(self.env)
        await self.update_report()

main = Main()
asyncio.run( main.start() )