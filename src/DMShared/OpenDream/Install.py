
from ..common import *

from . import Builder

class Install(object):
    @staticmethod
    def load(env, _id):
        install = env.prefix('.opendream.install')
        install.id = _id
        install.platform = 'opendream'
        env.attr.install = install

    async def install_opendream(env):
        genv = env.branch()
        genv.attr.git.repo.url = os.environ['OPENDREAM_REPO']
        genv.attr.git.repo.dir = env.attr.install.dir
        await Shared.Git.Repo.clone(genv)
        await Shared.Git.Repo.init_all_submodules(genv)

        benv = env.branch()
        benv.attr.dotnet.solution.path = env.attr.install.dir
        await Builder.build( benv )