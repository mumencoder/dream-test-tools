
from .common import *

class App(object):
    def __init__(self):
        pass

    def init(self):
        self.env = Shared.Environment()
        self.load_configs()

        self.env.attr.test_mode = "all"

        self.env.event_handlers['process.complete'] = self.handle_process_complete
        self.env.attr.resources.process = Shared.CountedResource(8)

        self.env.attr.resources.build = Shared.CountedResource(2)
        self.env.attr.state = Shared.FilesystemState(self.env.attr.dirs.state, 
            loader=lambda s: json.loads(s), saver=lambda js: json.dumps(js))

        Shared.Workflow.init( self.env )

        self.env.attr.dirs.ramdisc.ensure_clean_dir()
        self.env.attr.process.log_mode = "auto"
        self.env.attr.process.auto_log_path = self.env.attr.dirs.ramdisc / "auto_process_logs"
        self.env.attr.process.auto_logs = []

        self.env.attr.workflow.report_path = self.env.attr.dirs.ramdisc / "workflow_report.html"
        print(f"file://{self.env.attr.workflow.report_path}")

    async def deinit(self):
        pass

    async def start(self):
        self.init()
        try:
            await self.run()
        finally:
            os.system('stty sane')

    def load_configs(self):
        config_path = os.getenv("DTT_CONFIG_FILE")
        config_obj = Shared.Object.import_file( config_path )
        for name, attr in vars(config_obj).items():
            if name.startswith('setup_'):
                attr(self.env)

    def parse_install_arg(s):
        s = s.split(".")
        return {'platform':s[0], 'install_id':s[1]}

    @staticmethod
    async def handle_process_complete(env):
        process = env.prefix('.process')

        if process.log_mode == "auto":
            process.auto_logs.append( env )