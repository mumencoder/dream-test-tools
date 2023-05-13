
from ..common import *

from . import Download
from . import Compilation

class Install(object):
    @staticmethod
    async def from_zip(env):
        if not os.path.exists(env.attr.install.dir):
            penv = env.branch()
            penv.attr.shell.env = os.environ
            penv.attr.shell.command = f"unzip -qq {env.attr.install.zip_path} -d {env.attr.install.dir}"
            await Shared.Process.shell(penv)

    @staticmethod
    async def available(env):
        menv = env.branch()
        menv.attr.shell.command = Compilation.create_dreammaker_command( menv )
        Shared.Process.pipe_stdout(menv)
        await Compilation.invoke_compiler( menv )
        return menv.attr.process.instance.returncode == 1

    async def status_code(env):    
        if await Install.available( env ):
            return "exists"
        else:
            return "missing"
