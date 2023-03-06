
from ..common import *

from . import Download

class Install(object):
    @staticmethod
    async def from_zip(env):
        if not os.path.exists(env.attr.install.dir):
            penv = env.branch()
            penv.attr.shell.env = os.environ
            penv.attr.shell.command = f"unzip -qq {env.attr.install.save_path} -d {env.attr.install.dir}"
            penv.attr.process.stdout = open(env.attr.tmp_dir / 'byond.install.from_zip.txt', "w")
            await Shared.Process.shell(penv)
            if os.path.exists( env.attr.install.save_path ):
                os.remove( env.attr.install.save_path )

async def install(env):
    env = env.branch()
    env.attr.install.save_path = env.attr.tmp_dir / 'byond.zip'
    await Download.linux(env)
    await Install.from_zip(env)