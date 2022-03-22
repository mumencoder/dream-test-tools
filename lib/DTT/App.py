
import os, asyncio
import json
import Shared, Byond, ClopenDream, OpenDream

from .Resource import *

class App(object):
    def __init__(self):
        pass

    def init(self):
        self.env = Shared.Environment()
        self.load_configs()

        Shared.Workflow.init(self.env)
        self.env.attr.wf.id = Shared.Random.generate_string(8)
        self.env.attr.wf.root_dir = self.env.attr.dirs.ramdisc / "workflows" / self.env.attr.wf.id 
        self.env.attr.test_mode = "all"

        self.env.attr.process.log_mode = "auto"
        self.env.attr.process.auto_log_path = self.env.attr.wf.root_dir / "auto_process_logs"

        self.env.attr.resources.git = Shared.CountedResource(2)
        self.env.attr.resources.process = Shared.CountedResource(4)
        self.env.attr.resources.opendream_server = Shared.CountedResource(1)

        self.env.attr.resources.opendream_repo = OpenDreamRepoResource(self.env, limit=4)

        self.running = True

        self.task_report_path = self.env.attr.dirs.ramdisc / "task_report.html"
        print(f"file://{self.task_report_path}")

        for name in ["schedule", "github"]:
            state_file = self.env.attr.dirs.state / f'{name}.json'
            state = Shared.InfiniteDefaultDict()
            if os.path.exists(state_file):
                with open(state_file, "r") as f:
                    try:
                        state.initialize( json.load(f) )
                    except json.decoder.JSONDecodeError:
                        raise Exception(f"State decode error: {name}")
            getattr(self.env.attr, name).state = state

        self.setup_report_task(self.env)

    async def deinit(self):
        await self.update_report()
        for name in ["schedule", "github"]:
            state_file = self.env.attr.dirs.state / f'{name}.json'
            with open(state_file, "w") as f:
                json.dump( getattr(self.env.attr, name).state.finitize(), f)

    async def start(self):
        self.init()
        await self.run()
        await self.deinit()

    def load_configs(self):
        config_dir = os.path.abspath( os.path.expanduser("~/dream-storage/config") )
        for file_path in sorted(os.listdir( config_dir )):
            config_path = os.path.join(config_dir, file_path)
            config_obj = Shared.Object.import_file( config_path )
            for name, attr in vars(config_obj).items():
                if name.startswith('setup_'):
                    attr(self.env)

    async def update_report(self):
        with open(self.task_report_path, "w") as f:
            f.write( str(Shared.Workflow.Report.status(self.env)) )
        for wfenv in self.env.attr.workflows.values():
            with open(wfenv.attr.wf.log_path, "w") as f:
                f.write( str(Shared.Workflow.Report.wf_log( wfenv ) ) )

    async def update_report_loop(self):
        while self.running:
            await self.update_report()
            await asyncio.sleep(5.0)

    def parse_install_arg(s):
        s = s.split(".")
        return {'platform':s[0], 'install_id':s[1]}

    def setup_report_task(self, env):
        env = env.branch()
        Shared.Workflow.open(env, "report")
        Shared.Workflow.set_task(env, self.update_report_loop())
        env.attr.wf.background = True

    async def clopen_source(self, env):
        await ClopenDream.Source.ensure(env)
        await Shared.Git.Repo.init_all_submodules(env)

    async def build_pr(self, env):
        while True:
            resource = await env.attr.resources.opendream_repo.acquire()
            if resource is not None:
                data = resource["data"]
                break
            await asyncio.sleep(0.5)

        print(data, env.attr.git.repo.ref)
        try:        
            OpenDream.Source.load( env, data["id"] )
            env.attr.git.repo.local_dir = data["path"]
            env.attr.git.repo.url = 'https://github.com/wixoaGit/OpenDream'
            await Shared.Git.Repo.ensure(env)
            await Shared.Git.Repo.init_all_submodules(env)

            env.attr.opendream.build.mode = "publish"
            env.attr.dotnet.build.output_dir = env.attr.opendream.dirs.installs / f'github.opendream.wixoaGit.{env.attr.git.api.repo.head.commit}'
            await OpenDream.Builder.build( env )

            print( env.attr.git.api.repo.head.commit )
        finally:
            env.attr.resources.opendream_repo.release(resource)

    async def update_prs(self, env):
        env = env.branch()
        env.attr.github.endpoint = 'api.github.com'
        env.attr.github.owner = "wixoaGit"
        env.attr.github.repo = "OpenDream"
        env.attr.schedule.event_name = 'github.opendream.wixoaGit.pulls.update'
        if Shared.Scheduler.hourly(env):
            pulls_r = Shared.Github.list_pull_requests(env)
            env.attr.github.state['requests'][env.attr.schedule.event_name] = pulls_r
            Shared.Scheduler.update(env)

        for pull in env.attr.github.state['requests'][env.attr.schedule.event_name]:
            s_pull = env.attr.github.state['pulls'][ pull["number"] ]
            build = False
            if 'recent_build_sha' not in s_pull:
                build = True
            if build is True:
                build_env = env.branch()
                build_env.attr.git.repo.ref = pull["merge_commit_sha"]
                print(f"{pull['number']} {pull['merge_commit_sha']}")
                Shared.Workflow.open(build_env, f"build.pr.{pull['number']}")
                Shared.Workflow.set_task(build_env, self.build_pr(build_env) )
                
        await Shared.Workflow.run_all(self.env)

    async def prepare_empty_clopendream(self, env):
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

    async def build_clopendream(self, base_env, install_id):
        env = base_env.branch()
        ClopenDream.Source.load(env, install_id)
        env.attr.git.local_dir = env.attr.clopendream.source.dir
        Shared.Workflow.open(env, f"clopendream.source.{install_id}")
        Shared.Workflow.set_task(env, self.clopen_source(env) )

        await Shared.Workflow.run_all(self.env)

        env = base_env.branch()
        ClopenDream.Source.load(env, install_id)
        env.attr.clopendream.install.id = install_id
        env.attr.clopendream.install.dir = env.attr.clopendream.source.dir
        Shared.Workflow.open(env, f"clopendream.build.{install_id}")
        Shared.Workflow.set_task(env, ClopenDream.Builder.build(env) )

        await Shared.Workflow.run_all(self.env)
