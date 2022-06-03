
from .common import *

from .Install import *

class Byond(object):
    def load_install(env, version):
        Shared.Task.tags(env, {'platform':'byond', 'version':version} )
        async def task(penv, senv):
            senv.attr.platform_cls = base.Byond
            base.Byond.Install.load(senv, version)
            senv.attr.byond.install.version = version
            Install.config(senv)
        return Shared.Task( env, task, tags={'action':'load_install'})

    def download(env):
        env = env.branch()
        async def task(penv, senv):
            await base.Byond.Install.download(senv)
        return Shared.Task( env, task, tags={'action':'download'} )