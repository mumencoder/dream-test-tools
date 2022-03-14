
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def clopen_source(self, env):
        await ClopenDream.Source.ensure(env)
        await Shared.Git.Repo.init_all_submodules(env)

    async def run(self):
        env = self.env.branch()
        self.setup_report_task(env)

        clenv = env.branch()
        ClopenDream.Source.load(clenv, 'currentdev')
        clenv.attr.git.local_dir = clenv.attr.clopendream.source.dir
        Shared.Workflow.open(clenv, f"clopendream.source")
        Shared.Workflow.set_task(clenv, self.clopen_source(clenv) )

        await Shared.Workflow.run_all(self.env)

        clenv = env.branch()
        ClopenDream.Source.load(clenv, 'currentdev')
        clenv.attr.clopendream.install.id = 'currentdev'
        clenv.attr.clopendream.install.dir = clenv.attr.clopendream.source.dir
        clenv.attr.install = clenv.attr.clopendream.install
        clenv.attr.install.platform = "clopendream"
        Shared.Workflow.open(clenv, f"clopendream.build")
        Shared.Workflow.set_task(clenv, ClopenDream.Builder.build(clenv) )

        await Shared.Workflow.run_all(self.env)

        for tenv in test_runner.list_all_tests(env, self.env.attr.tests.dirs.dm_files):
            clenv = tenv.branch()
            clenv.attr.install.platform = 'clopendream'
            clenv.attr.install.id = "currentdev"
            ClopenDream.Source.load(clenv, 'currentdev')
            test_runner.Curated.load_test( clenv )

            clod_json_path = clenv.attr.test.base_dir / 'clopen_ast.json'
            if not os.path.exists(clod_json_path):
                continue
            clenv.attr.clopendream.ast1 = clod_json_path
            clenv.attr.clopendream.install.working_dir = clenv.attr.test.base_dir
            clenv.attr.clopendream.install.dir = clenv.attr.clopendream.source.dir

            oenv = tenv.branch()
            oenv.attr.install.platform = 'opendream'
            oenv.attr.install.id = 'clopendream'
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