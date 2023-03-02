
from .imports import *

### helpers
def print_env(env, title):
    print(f"=== {title}")
    for prop in env.unique_properties():
        print(prop, type(env.get_attr(prop)))

class Counter(object):
    def __init__(self):
        self.c = 0
        self.visible_states = [2 ** x for x in range(0,11)]
        self.visible = False

    def inc(self, n=1):
        self.c += n
        self.update_state()
        
    def update_state(self):
        if self.c in self.visible_states or self.c % self.visible_states[-1] == 0:
            self.visible = True
        else:
            self.visible = False

    def state(self):
        return self.visible
    
### config
def load_config(env):
    if os.path.exists('server_config.yaml'):
        with open( 'server_config.yaml', "r") as f:
            config = yaml.load( f, yaml.Loader )
        for path_id, path in config["paths"].items():
            config["paths"][path_id] = Shared.Path( path )
    else:
        raise Exception("cannot read config")
    env.attr.config = config
    env.attr.dirs.tmp = Shared.Path( env.attr.config["paths"]["tmp"] )

def setup_base(env):
    env.attr.shell.env = os.environ
    env.attr.process.stdout = sys.stdout

### tasks
def new_task(fn, *args, **kwargs):
    pending_tasks.append( (fn, args, kwargs) )

def async_thread_launch():
    asyncio.run( async_thread_main() )

async def async_thread_main():
    global pending_tasks, tasks
   
    while True:
        for fn, args, kwargs in pending_tasks:
            tasks.add( asyncio.create_task( fn(*args, **kwargs) ) )
        pending_tasks = []

        try:
            for co in asyncio.as_completed(tasks, timeout=0.1):
                await co
        except TimeoutError:
            pass
        
        remaining_tasks = set()
        for task in tasks:
            if not task.done():
                remaining_tasks.add( task )
            else:
                pass
        tasks = remaining_tasks