
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        env = self.env.branch()

        report_env = env.branch()
        Shared.Workflow.open(report_env, "report")
        Shared.Workflow.set_task(report_env, self.update_report_loop())
        report_env.attr.wf.background = True

        env = self.env.branch()
        Byond.Install.load(env, 'default')
        for env in test_runner.list_all_tests(env, main.env.attr.tests.dirs.dm_files):
            env.attr.install = env.attr.byond.install
            env.attr.install.platform = "byond"
            test_runner.Curated.load_test( env )
            test_runner.Curated.prepare_test( env )
            test_runner.generate_test( env )
            Shared.Workflow.open(env, f"test.byond.{env.attr.test.id}")
            Shared.Workflow.set_task(env, test_runner.byond.do_test(env) )

        env = self.env.branch()
        env.attr.opendream.sources['default_full'] = env.attr.opendream.sources['default']
        OpenDream.Source.load(env, 'default_full')
        env.attr.opendream.install.id = 'default_full'
        env.attr.opendream.install.dir = env.attr.opendream.source.dir
        env.attr.install = env.attr.opendream.install
        env.attr.install.platform = "opendream"
        for env in test_runner.list_all_tests(env, main.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( env )
            test_runner.Curated.prepare_test( env )
            test_runner.generate_test( env )
            Shared.Workflow.open(env, f"test.opendream.{env.attr.test.id}")
            Shared.Workflow.set_task(env, test_runner.opendream.do_test(env) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        return

        i = 0
        base_env = self.env.branch()
        for pr in env.attr.state['github_prs']['data']:
            env = base_env.branch()
            repo_name = pr["head"]["repo"]["full_name"].replace("/", ".")
            pr_sha = pr["head"]["sha"]
            install_id = f'github.{repo_name}.{pr_sha}'
            info = Shared.Github.pull_request_to_install(pr)
            env.attr.opendream.sources[install_id] = info
            OpenDream.Source.load(env, install_id)
            env.attr.opendream.install.id = install_id
            env.attr.opendream.install.dir = env.attr.opendream.source.dir
            env.attr.install = env.attr.opendream.install
            env.attr.install.platform = "opendream"

            if not os.path.exists( OpenDream.Compilation.get_exe_path(env) ):
                print("skip", install_id)
                continue

            for env in test_runner.list_all_tests(env, main.env.attr.tests.dirs.dm_files):
                test_runner.Curated.load_test( env )
                test_runner.Curated.prepare_test( env )
                test_runner.generate_test( env )
                Shared.Workflow.open(env, f"test.opendream.{env.attr.test.id}.{i}")
                Shared.Workflow.set_task(env, test_runner.opendream.do_test(env) )
                i += 1

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        self.running = False
        os.system('stty sane')

main = Main()
asyncio.run( main.start() )