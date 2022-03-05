
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
        env.attr.opendream.sources['default_full'] = env.attr.opendream.sources['default']
        env.attr.git.repo.clone_depth = 512
        OpenDream.Source.load(env, 'default_full')
        Shared.Workflow.open(env, f"opendream.full")
        Shared.Workflow.set_task(env, OpenDream.Source.ensure(env) )
        await Shared.Workflow.run_all(self.env)
        await self.update_report()

        env.attr.github.endpoint = 'api.github.com'
        env.attr.github.owner = "wixoaGit"
        env.attr.github.repo = "OpenDream"
        github_prs = env.attr.state.get('github_prs', None)
        if github_prs is None:
            github_prs = {"update_time":0}
        if time.time() - github_prs['update_time'] > 60*60:
            github_prs['data'] = Shared.Github.list_pull_requests(env)
            github_prs['update_time'] = time.time()
        env.attr.state['github_prs'] = github_prs

        for pr in env.attr.state['github_prs']['data']:
            env = self.env.branch()

            repo_name = pr["head"]["repo"]["full_name"].replace("/", ".")
            pr_sha = pr["head"]["sha"]
            install_id = f'github.{repo_name}.{pr_sha}'
            info = Shared.Github.pull_request_to_install(pr)
            env.attr.opendream.sources[install_id] = info

            denv = self.env.branch()
            OpenDream.Source.load(denv, 'default_full')

            env.attr.opendream.sources[install_id] = {'type':'pr', 'base_location': denv.attr.opendream.source.dir, 'pr':pr }

        i = 0
        for install_id, info in env.attr.opendream.sources.items():
            env2 = env.branch()
            OpenDream.Source.load(env2, install_id)
            Shared.Workflow.open(env2, f"opendream.source.{install_id}")
            Shared.Workflow.set_task(env2, OpenDream.Source.ensure(env2) )
            i += 1
        await Shared.Workflow.run_all(self.env)

        i = 0
        for install_id, info in env.attr.opendream.sources.items():
            if env.attr.workflows[f'opendream.source.{install_id}'].attr.state == "exception":
                continue
            env2 = env.branch()
            OpenDream.Source.load(env2, install_id)
            Shared.Workflow.open(env2, f"opendream.build.{i}")
            Shared.Workflow.set_task(env2, OpenDream.Builder.build(env2) )
            i += 1
        await Shared.Workflow.run_all(self.env)

        self.running = False
        await self.update_report()

main = Main()
asyncio.run( main.start() )