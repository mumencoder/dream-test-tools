
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, SS13, Shared

from DTT import App
import test_runner

class Main(App):
    async def setup_source(self, env):
        await OpenDream.Source.ensure(env) 
        await Shared.Git.Repo.init_all_submodules(env)

    async def run(self):
        env = self.env.branch()

        oenv = env.branch()
        OpenDream.Source.load(oenv, 'currentdev')
        oenv.attr.opendream.install.dir = oenv.attr.opendream.source.dir
        Shared.Workflow.open(oenv, f"opendream.source")
        Shared.Workflow.set_task(oenv, self.setup_source(oenv) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        build_env = oenv.branch()
        Shared.Workflow.open(build_env, f"opendream.build")
        Shared.Workflow.set_task(build_env, OpenDream.Builder.build(build_env) )

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        for repo_name, repo in env.attr.ss13.sources.items():
            ssenv = oenv.branch()

            ssenv.attr.ss13.base_dir = env.attr.ss13.dirs.installs / repo_name
            SS13.Install.find_dme( ssenv )
            print(repo_name, ssenv.attr.ss13.dme_file)
            if ssenv.attr.ss13.dme_file is None:
                continue

            ssenv.attr.opendream.compilation.dm_file = ssenv.attr.ss13.dme_file
            ssenv.attr.opendream.compilation.args = {'flags':['experimental-preproc', 'verbose']}
            Shared.Workflow.open(ssenv, f"ss13.compile.{repo_name}")
            Shared.Workflow.set_task(ssenv, OpenDream.Compilation.compile(ssenv))

        await Shared.Workflow.run_all(self.env)
        await self.update_report()

main = Main()
asyncio.run( main.start() )