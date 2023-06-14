
from .imports import *

def base_env():
    env = Shared.Environment()
    env.attr.shell.env = os.environ
    env.attr.process.events = Shared.EventManager()
    return env

def load_config(env, configfile, base_fn):
    print("load config...")
    with open(configfile, "r") as f:
        gs = {}
        exec( compile(f.read(), configfile, 'exec'), gs )
        config = gs["load"]()

    def assign_path(prefix, k, v):
        setattr(prefix, k, Shared.Path(v) )

    env.zip_with_dict( config["dirs"], assign_fn=assign_path, prefix=env.prefix('.dirs') )

    gs[base_fn](env)



