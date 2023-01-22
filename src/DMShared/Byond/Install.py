
from ..common import *

from . import Download

class Install(object):
    @staticmethod
    async def from_zip(env):
        if not os.path.exists(env.attr.install.dir):
            penv = env.branch()
            penv.attr.shell.env = os.environ
            penv.attr.shell.command = f"unzip -qq {env.attr.install.save_path} -d {env.attr.install.dir}"
            penv.attr.process.stdout = open(env.attr.dirs.tmp / 'byond.install.from_zip.txt', "w")
            await Shared.Process.shell(penv)
            if os.path.exists( env.attr.install.save_path ):
                os.remove( env.attr.install.save_path )

def load(env, data):
    env.attr.install.dir = Shared.Path( data["dir"] )
    env.attr.version.major = data["version"]["major"]
    env.attr.version.minor = data["version"]["minor"]

async def install(env):
    env = env.branch()
    env.attr.install.save_path = env.attr.dirs.tmp / 'byond.zip'
    await Download.linux(env)
    await Install.from_zip(env)