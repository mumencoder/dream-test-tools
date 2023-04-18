
from ..imports import *
from ..env import *
from ..resources import *

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
    status = await Shared.Git.Repo.status(env)

    if status is None:
        return "missing"
    
    if int(status['branch.ab'][0]) == 0 and int(status['branch.ab'][1]) == -1:
        return "behind_upstream"

    sstatus = await Shared.Git.Repo.submodule_status(env)
    for name, state in sstatus.items():
        if state == 'missing':
            return "submodule_missing"

    metadata = maybe_from_pickle( get_file(env.attr.metadata_dir / 'resources' / install_id / 'build.pckl'), default_value={} )
    if 'last_build_commit' not in metadata:
        return "nobuild"

    if metadata['last_build_commit'] != status['branch.oid']:
        return "oldbuild"
    
    return "ready"

async def status_dream_repo(env, repo_id):
    env = env.branch()
    load_dream_repo(env, repo_id)

    status = await Shared.Git.Repo.status(env)

    if status is None:
        return "missing"
    
    return "ready"

def load_byond_install(env, install_id):
    for prop in list(env.attr.config.filter_properties(f".{install_id}.*")):
        env.attr.config.rebase(f".{install_id}", ".install", prop, new_env=env, copy=True)

def load_opendream_install(env, install_id):
    DMShared.OpenDream.Install.load_repo(env, env.attr.config.prefix(f".{install_id}") )
    DMShared.OpenDream.Install.load_install_from_repo(env)

def load_dream_repo(env, repo_id):
    DMShared.OpenDream.Install.load_repo(env, env.attr.config.prefix(f".{repo_id}") )

import DMShared, DreamCollider