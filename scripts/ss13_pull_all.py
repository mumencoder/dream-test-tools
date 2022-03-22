
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        env = self.env.branch()

        for repo_name, repo in env.attr.ss13.sources.items():
            env = self.env.branch()

            env.attr.git.repo.local_dir = env.attr.ss13.dirs.installs / repo_name
            env.attr.git.repo.url = repo["url"]
            if "branch" in repo:
                env.attr.git.repo.branch = repo["branch"]

            Shared.Workflow.open(env, f"ss13.{repo_name}")
            Shared.Workflow.set_task(env, Shared.Git.Repo.ensure(env) )

        await Shared.Workflow.run_all(self.env)
        self.running = False
        await self.update_report()

main = Main()
asyncio.run( main.start() )