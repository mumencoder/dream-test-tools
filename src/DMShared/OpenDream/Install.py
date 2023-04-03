
from ..common import *

from . import Builder

class Install(object):
    @staticmethod
    def load_repo(env, data):
        env.attr.git.repo.url = data.url
        env.attr.git.repo.dir = Shared.Path( data.path )

    async def init_repo(env):
        await Shared.Git.Repo.clone(env)
        await Shared.Git.Repo.init_all_submodules(env)

    def load_install_from_repo(env):
        env.attr.install.dir = env.attr.git.repo.dir

