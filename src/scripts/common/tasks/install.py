
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

def load_byond_install(root_env, verbose=False):
    benv = root_env.branch()
    benv_t = EnvTracker(benv, "benv")
    for prop in list(root_env.attr.config.filter_properties(".byond_main.*")):
        root_env.attr.config.rebase(".byond_main", ".install", prop, new_env=benv, copy=True)
    if verbose:
        benv_t.print("1")
    return benv

import DMShared, DreamCollider