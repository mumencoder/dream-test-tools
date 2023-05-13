
from ..common import *

from . import Builder

class Install(object):
    @staticmethod
    def load_repo(env, data):
        env.attr.git.repo.url = data.url
        env.attr.git.repo.dir = data.path

    def load_install_from_repo(env):
        env.attr.install.dir = env.attr.git.repo.dir

    async def build_status_code(env):
        metadata = Shared.maybe_from_pickle( Shared.get_file(env.attr.opendream.build_metadata), default_value={} )
        if 'last_build_commit' not in metadata:
            return "nobuild"

        if metadata['last_build_commit'] != env.attr.git.status['branch.oid']:
            return "oldbuild"
        
        return "ready"
    
    async def update_repo(base_env):
        if status in ["nobuild", "oldbuild"]:
            await build_opendream(env, env.attr.opendream.build_metadata)

