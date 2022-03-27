
import os, asyncio
import json, shutil
import Shared, Byond, ClopenDream, OpenDream, SS13

import test_runner

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

        self.env.attr.git.repo.remote = "origin"

        self.env.attr.resources.git = Shared.CountedResource(2)
        self.env.attr.resources.process = Shared.CountedResource(4)
        self.env.attr.resources.opendream_server = Shared.CountedResource(1)
        self.env.attr.resources.ss13 = Shared.CountedResource(2)

        self.env.attr.resources.opendream_repo = OpenDreamRepoResource(self.env, limit=4)

        self.running = True

        self.task_report_path = self.env.attr.dirs.ramdisc / "task_report.html"
        print(f"file://{self.task_report_path}")

        for name in ["schedule", "github", "tests"]:
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
        for name in ["schedule", "github", "tests"]:
            state_file = self.env.attr.dirs.state / f'{name}.json'
            result = json.dumps( getattr(self.env.attr, name).state.finitize(), cls=Shared.Json.BetterEncoder)
            with open(state_file, "w") as f:
                f.write( result )

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

    async def build_shared_opendream(self, env):
        while True:
            resource = await env.attr.resources.opendream_repo.acquire()
            if resource is not None:
                data = resource["data"]
                break
            await asyncio.sleep(0.5)

        try:        
            OpenDream.Source.load( env, data["id"] )
            env.attr.git.repo.local_dir = data["path"]
            env.attr.git.repo.url = 'https://github.com/wixoaGit/OpenDream'
            await Shared.Git.Repo.ensure(env)
            await Shared.Git.Repo.init_all_submodules(env)

            Shared.Path.sync_folders( env.attr.opendream.source.dir, env.attr.opendream.install.dir )
            env.attr.dotnet.solution.path = env.attr.opendream.install.dir
            await OpenDream.Builder.build( env )
        finally:
            env.attr.resources.opendream_repo.release(resource)

    async def update_repo(self, env):
        if Shared.Scheduler.hourly(env):
            env.attr.git.repo.remote_ref = 'HEAD'
            await Shared.Git.Repo.ensure(env)
            # TODO: this might break on submodule version updates
            await Shared.Git.Repo.init_all_submodules(env)
            Shared.Scheduler.update(env)

    async def update_mains(self, base_env):
        env = base_env.branch()
        OpenDream.Source.load(env, 'main')
        env.attr.opendream.source.location = 'https://github.com/wixoaGit/OpenDream'
        env.attr.schedule.event_name = 'update.mains.opendream'
        Shared.Workflow.open(env, f"update.mains.opendream")
        Shared.Workflow.set_task(env, self.ensure_opendream(env, env.attr.opendream.source) )

        env = base_env.branch()
        OpenDream.Source.load(env, 'ClopenDream-compat')
        env.attr.opendream.source.location = 'https://github.com/mumencoder/OpenDream'
        env.attr.git.repo.branch = {'remote':'origin', 'name':'ClopenDream-compat'}
        env.attr.schedule.event_name = 'update.mains.opendream.clopendream-compat'
        Shared.Workflow.open(env, f"update.mains.opendream.clopendream-compat")
        Shared.Workflow.set_task(env, self.ensure_opendream(env, env.attr.opendream.source) )

        env = base_env.branch()
        ClopenDream.Source.load(env, 'main')
        env.attr.clopendream.source.location = 'https://github.com/mumencoder/Clopendream-parser'
        env.attr.schedule.event_name = 'update.mains.clopendream'
        Shared.Workflow.open(env, f"update.mains.clopendream")
        Shared.Workflow.set_task(env, self.ensure_clopendream(env, env.attr.clopendream.source) )

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
                OpenDream.Install.load(build_env, f'github.wixoaGit.pr.{pull["merge_commit_sha"]}')
                build_env.attr.git.repo.remote_ref = pull["merge_commit_sha"]
                print(f"{pull['number']} {pull['merge_commit_sha']}")
                Shared.Workflow.open(build_env, f"build.pr.{pull['number']}")
                Shared.Workflow.set_task(build_env, self.build_shared_opendream(build_env) )
                
    async def run_tests(self, env):
        for tenv in test_runner.list_all_tests(env, self.env.attr.tests.dirs.dm_files):
            test_runner.Curated.load_test( tenv )
            test_runner.Curated.prepare_test( tenv )
            test_runner.generate_test( tenv )
            Shared.Workflow.open(tenv, f"{tenv.attr.test.prefix}.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, tenv.attr.test.runner(tenv) )

    async def prepare_empty_clopendream(self, env):
        empty_dir = env.attr.dirs.state / 'empty'
        with open(env.attr.dirs.state / 'empty' / 'empty.dm', "w") as f:
            f.write('\n')

        benv = env.branch()
        Byond.Install.load(benv, 'main')
        benv.attr.byond.compilation.file_path = empty_dir / 'empty.dm'
        benv.attr.byond.compilation.out = empty_dir / 'empty.codetree'
        await Byond.Compilation.generate_code_tree(benv)

    async def ensure_opendream(self, base_env, source):
        env = base_env.branch()
        OpenDream.Source.load(env, source.id)
        env.attr.git.repo.url = source.location
        env.attr.git.repo.local_dir = env.attr.opendream.source.dir

        await Shared.Git.Repo.ensure(env)
        await Shared.Git.Repo.init_all_submodules(env)

        OpenDream.Install.load(env, source.id)
        await self.build_opendream(env)

    async def ensure_clopendream(self, base_env, source):
        env = base_env.branch()
        ClopenDream.Source.load(env, source.id)
        env.attr.git.repo.url = source.location
        env.attr.git.repo.local_dir = env.attr.clopendream.source.dir

        await Shared.Git.Repo.ensure(env)
        await Shared.Git.Repo.init_all_submodules(env)

        ClopenDream.Install.load(env, source.id)
        await self.build_clopendream(env)

    async def build_opendream(self, base_env):
        env = base_env.branch()
        Shared.Path.sync_folders( env.attr.opendream.source.dir, env.attr.opendream.install.dir )
        env.attr.dotnet.solution.path = env.attr.opendream.install.dir
        await OpenDream.Builder.build(env)

    async def build_clopendream(self, base_env):
        env = base_env.branch()
        await ClopenDream.Builder.build(env)
        Shared.Path.sync_folders( env.attr.clopendream.source.dir, env.attr.clopendream.install.dir )
        ClopenDream.Install.copy_stdlib(env)
        await self.prepare_empty_clopendream(env)

    def load_ss13_test(self, env):
        env.attr.test.root_dir = env.attr.tests.dirs.output / f'ss13.{env.attr.ss13.repo_name}'
        env.attr.test.base_dir = env.attr.test.root_dir / f'{env.attr.install.platform}.{env.attr.install.id}'

    def iter_ss13_tests(self, env):
        for repo_name, repo in self.env.attr.ss13.sources.items():
            ssenv = env.branch()

            ssenv.attr.ss13.repo_name = repo_name
            ssenv.attr.ss13.base_dir = self.env.attr.ss13.dirs.installs / repo_name
            SS13.Install.find_dme( ssenv )
            if ssenv.attr.ss13.dme_file is None:
                continue

            yield ssenv

    def prepare_parse_clopendream_test(self, tenv, clopen_id):
        btenv = tenv.branch()
        Byond.Install.load(btenv, 'main')
        test_runner.Curated.load_test( btenv )
        btenv.attr.byond.compilation.out = btenv.attr.test.base_dir / 'test.codetree'

        ctenv = tenv.branch()
        ClopenDream.Install.load(ctenv, clopen_id)
        ctenv.attr.byond.codetree = btenv.attr.byond.compilation.out
        yield btenv, ctenv

    def prepare_parse_clopendream_ss13(self, ssenv, clopen_id):
        btenv = ssenv.branch()
        Byond.Install.load(btenv, 'main')
        self.load_ss13_test(btenv)
        btenv.attr.byond.compilation.out = btenv.attr.test.base_dir / 'ss13.codetree'

        ctenv = ssenv.branch()
        ClopenDream.Install.load(ctenv, clopen_id)
        self.load_ss13_test(ctenv)
        ctenv.attr.clopendream.install.working_dir = ctenv.attr.test.base_dir
        ctenv.attr.byond.codetree = btenv.attr.byond.compilation.out
        yield btenv, ctenv

    async def parse_clopendream_test(self, tenv, clopen_id):
        btenv, ctenv = self.prepare_parse_clopendream_test(tenv, clopen_id)
        test_runner.Curated.prepare_test( btenv )
        test_runner.generate_test( btenv )
        await Byond.Compilation.generate_code_tree(btenv)

        await ClopenDream.Install.parse(ctenv)
    
    async def parse_clopendream_ss13(self, ssenv, clopen_id):
        try:
            await self.env.attr.resources.ss13.acquire(ssenv)

            btenv, ctenv = self.prepare_parse_clopendream_ss13(ssenv, clopen_id)

            await Byond.Compilation.generate_code_tree(btenv)

            await ClopenDream.Install.parse(ctenv)
        finally:
            self.env.attr.resources.ss13.release(ssenv)

    async def parse_opendream_ss13(self, ssenv, open_id):
        try:
            await self.env.attr.resources.ss13.acquire(ssenv)
            await OpenDream.Compilation.compile(ssenv)
            self.load_ss13_test(ssenv)
            shutil.move( ssenv.attr.ss13.base_dir / "ast.json", ssenv.attr.test.base_dir / "ast.json")
        finally:
            self.env.attr.resources.ss13.release(ssenv)
