
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

        empty_dir = env.attr.dirs.state / 'empty'
        clenv.attr.clopendream.config = {'empty_dir': empty_dir }
        ClopenDream.Install.write_config( clenv )
        with open(clenv.attr.dirs.state / 'empty' / 'empty.dm', "w") as f:
            f.write('\n')

        benv = env.branch()
        Byond.Install.load(benv, 'default')
        benv.attr.byond.compilation.file_path = clenv.attr.clopendream.config['empty_dir'] / 'empty.dm'
        benv.attr.byond.compilation.out = clenv.attr.clopendream.config['empty_dir'] / 'empty.codetree'
        Shared.Workflow.open(benv, f"test.byond.empty")
        Shared.Workflow.set_task(benv, Byond.Compilation.generate_code_tree(benv) )

        await Shared.Workflow.run_all(self.env)

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