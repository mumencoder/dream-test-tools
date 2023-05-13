
from ..imports import *
from ..env import *
from ..resources import *

def load_byond_install(env, install_id):
    for prop in list(env.attr.config.filter_properties(f".{install_id}.*")):
        env.attr.config.rebase(f".{install_id}", ".install", prop, new_env=env, copy=True)

def load_opendream_install(env, install_id):
    DMShared.OpenDream.Install.load_repo(env, env.attr.config.prefix(f".{install_id}") )
    DMShared.OpenDream.Install.load_install_from_repo(env)

def load_dream_repo(env, repo_id):
    DMShared.OpenDream.Install.load_repo(env, env.attr.config.prefix(f".{repo_id}") )

import DMShared, DreamCollider