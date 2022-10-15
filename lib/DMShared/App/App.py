
from .common import *

class App(object):
    def __init__(self):
        self.env = Shared.Environment()

    def init(self):
        self.load_configs()

        self.env.test_mode = "all"
        self.env.state.tasks = Shared.FilesystemState( self.env.dirs.state / 'tasks', 
            loader=lambda s: json.loads(s), saver=lambda js: json.dumps(js) )
        self.env.state.results = Shared.FilesystemState( self.attr.dirs.state / 'results',
            loader=lambda s: json.loads(s), saver=lambda js: json.dumps(js) )

        async def handle_process_complete(env):
            process = env.prefix('.process')

            if process.log_mode == "auto":
                process.auto_logs.append( env )
        Shared.Env.handle_event('process.complete', self.handle_process_complete)

        self.env.resources.git = Shared.CountedResource(2)
        self.env.resources.build = Shared.CountedResource(2)
        self.env.resources.process = Shared.CountedResource(8)

        Shared.Workflow.init( self.env )
        Shared.Scheduler.init( self.env )

        self.env.dirs.ramdisc.ensure_clean_dir()
        self.env.process.log_mode = "auto"
        self.env.process.auto_log_path = self.env.dirs.ramdisc / "auto_process_logs"
        self.env.process.auto_logs = []

        self.env.workflow.report_path = self.env.dirs.ramdisc / "workflow_report.html"
        print(f"file://{self.env.workflow.report_path}")

        self.load_states(self.env)

    def init_top(self):
        self.tasks = {}

        env = self.env.branch()
        async def cleanup_opendream(senv):
            if senv.attr.platform_cls is OpenDream:
                shutil.rmtree( senv.attr.build.dir )
        self.env.event_handlers['tests.completed'] = cleanup_opendream

    def load_states(self, env):
        for name in os.listdir(env.attr.dirs.state + 'app'):
            state_filename = env.attr.dirs.state / 'app' / f'{name}.json'
            state = Shared.InfiniteDefaultDict()
            with Shared.File.open(state_filename, "r") as f:
                try:
                    state.initialize( json.load(f) )
                except json.decoder.JSONDecodeError:
                    raise Exception(f"State decode error: {name}")
            env.set_attr(name, state)

    def save_states(self, env):
        for name in env.filter_properties(".state.app.*"):
            state_filename = env.attr.dirs.state / 'app' / f'{name}.json'
            result = json.dumps( env.get_attr(name).finitize(), cls=Shared.Json.BetterEncoder)
            with Shared.File.open(state_filename, "w") as f:
                f.write( result )

    async def deinit(self):
        self.save_states(self.env)
        Shared.Scheduler.deinit(self.env)

    async def start(self):
        self.init()
        try:
            await self.run()
        finally:
            await self.deinit()
            os.system('stty sane')

    def load_configs(self):
        config_path = os.getenv("DTT_CONFIG_FILE")
        config_obj = Shared.Object.import_file( config_path )
        for name, attr in vars(config_obj).items():
            if name.startswith('setup_'):
                attr(self.env)

