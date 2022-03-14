
import os, asyncio
import json
import Shared, Byond, ClopenDream, OpenDream

class App(object):
    def __init__(self):
        pass

    def init(self):
        self.env = Shared.Environment()
        self.load_configs()

        Shared.Workflow.init(self.env)

        self.env.attr.test_mode = "all"

        self.env.attr.process.log_mode = "auto"
        self.env.attr.task_config.log_dir = self.env.attr.dirs.ramdisc / "task_logs"
        self.env.attr.git.repo.clone_depth = 1
        
        self.env.attr.resources.git = Shared.CountedResource(2)
        self.env.attr.resources.process = Shared.CountedResource(4)
        self.env.attr.resources.opendream_server = Shared.CountedResource(1)

        self.running = True

        self.task_report_path = self.env.attr.dirs.ramdisc / "task_report.html"
        print(f"file://{self.task_report_path}")

        self.state_file = self.env.attr.dirs.state / "app.json"
        if not os.path.exists(self.state_file):
            self.env.attr.state = {}
        else:
            with open(self.state_file, "r") as f:
                try:
                    self.env.attr.state = json.load(f)
                except json.decoder.JSONDecodeError:
                    print("Warning: state decode error")
                    self.env.attr.state = {}
                
    def deinit(self):
        with open(self.state_file, "w") as f:
            json.dump(self.env.attr.state, f)

    async def start(self):
        self.init()
        await self.run()
        self.deinit()

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

    async def install(self, env, platform, install_id):
        if platform == "byond":
            Byond.Install.load(env, install_id)
            await Byond.Install.ensure(env)
        elif platform == "opendream":
            OpenDream.Install.load(env, install_id)
            await OpenDream.Install.ensure(env)
        elif platform == "clopendream":
            ClopenDream.Install.load(env, install_id)
            await ClopenDream.Install.ensure(env)
        else:
            raise Exception("unknown install")

    def setup_report_task(self, env):
        env = env.branch()
        Shared.Workflow.open(env, "report")
        Shared.Workflow.set_task(env, self.update_report_loop())
        env.attr.wf.background = True
