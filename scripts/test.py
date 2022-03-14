
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def do(self, env):
        await OpenDream.Source.ensure(env)
        await Shared.Git.Repo.init_all_submodules(env)

    async def run(self):
        env = self.env.branch()
        self.setup_report_task(env)

        env2 = env.branch()
        OpenDream.Source.load(env2, 'clopendream')
        env2.attr.git.local_dir = env2.attr.opendream.source.dir
        Shared.Workflow.open(env2, f"opendream.source")
        Shared.Workflow.set_task(env2, self.do(env2) )

        await Shared.Workflow.run_all(self.env)

        env2 = env.branch()
        OpenDream.Source.load(env2, 'clopendream')
        env2.attr.opendream.install.id = 'clopendream'
        env2.attr.opendream.install.dir = env2.attr.opendream.source.dir
        env2.attr.install = env2.attr.opendream.install
        env2.attr.install.platform = "opendream"
        Shared.Workflow.open(env2, f"opendream.build")
        Shared.Workflow.set_task(env2, OpenDream.Builder.build(env2) )

        await Shared.Workflow.run_all(self.env)

        for tenv in test_runner.list_all_tests(env2, main.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( tenv )
            test_runner.Curated.prepare_test( tenv )
            test_runner.generate_test( tenv )
            tenv.attr.opendream.compilation.args = {"flags":['dump-ast']}
            Shared.Workflow.open(tenv, f"test.opendream.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, test_runner.opendream.do_test(tenv) )

        await Shared.Workflow.run_all(self.env)
        self.running = False
        await self.update_report()

main = Main()
asyncio.run( main.start() )