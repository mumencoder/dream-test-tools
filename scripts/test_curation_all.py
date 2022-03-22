
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

import time

class Main(App):
    async def run(self):
        env = self.env.branch()
        Byond.Install.load(env, 'default')
        for env in test_runner.list_all_tests(env, self.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( env )
            test_runner.Curated.prepare_test( env )
            test_runner.generate_test( env )
            Shared.Workflow.open(env, f"test.byond.{env.attr.test.id}")
            Shared.Workflow.set_task(env, test_runner.byond.do_test(env) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        env = self.env.branch()
        async def opendream_compile(base_env):
            env = base_env.branch()
            OpenDream.Source.load(env, 'main')
            env.attr.git.repo.local_dir = env.attr.opendream.source.dir
            env.attr.git.repo.url = 'https://github.com/wixoaGit/OpenDream'
            await Shared.Git.Repo.ensure(env)
            await Shared.Git.Repo.init_all_submodules(env)

            OpenDream.Install.load(env, 'main')
            env.attr.opendream.build.mode = "publish"
            env.attr.dotnet.build.output_dir = env.attr.opendream.install.dir
            await OpenDream.Builder.build( env )

        Shared.Workflow.open(env, f"opendream.compile")
        Shared.Workflow.set_task(env, opendream_compile(env) )
        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        start_time = time.time()
        for env in test_runner.list_all_tests(env, self.env.attr.tests.dirs.dm_files):
            OpenDream.Install.load( env, 'main' )
            test_runner.Curated.load_test( env )
            test_runner.Curated.prepare_test( env )
            test_runner.generate_test( env )
            Shared.Workflow.open(env, f"test.opendream.{env.attr.test.id}")
            Shared.Workflow.set_task(env, test_runner.opendream.do_test(env) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        print(time.time() - start_time)

        self.running = False
        os.system('stty sane')

main = Main()
asyncio.run( main.start() )