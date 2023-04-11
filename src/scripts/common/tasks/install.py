
from ..imports import *
from ..env import *

async def install_byond(benv):
    benv.attr.process.stdout = io.StringIO()
    benv.attr.process.stderr = benv.attr.process.stdout
    benv.attr.process.piped = True

    await DMShared.Byond.install(benv)

async def install_opendream(oenv):
    oenv.attr.process.stdout = io.StringIO()
    oenv.attr.process.stderr = oenv.attr.process.stdout
    oenv.attr.process.piped = True

    await DMShared.OpenDream.Install.init_repo(oenv)
    await DMShared.OpenDream.Builder.build(oenv)

async def status_byond_install(env, install_id):
    env = env.branch()
    load_byond_install(env, install_id)
    if await DMShared.Byond.Install.available( env ):
        return "exists"
    else:
        return "missing"

async def status_opendream_repo(env, install_id):
    env = env.branch()
    load_opendream_install(env, install_id)
    state = "missing"
    if not Shared.Git.Repo.exists(env):
        return state
    state = "exists"
    return state

def load_byond_install(env, install_id):
    for prop in list(env.attr.config.filter_properties(f".{install_id}.*")):
        env.attr.config.rebase(f".{install_id}", ".install", prop, new_env=env, copy=True)

def load_opendream_install(env, install_id):
    DMShared.OpenDream.Install.load_repo(env, env.attr.config.prefix(f".{install_id}") )
    DMShared.OpenDream.Install.load_install_from_repo(env)

import DMShared, DreamCollider