
from .common import *

from .Tests import *

class Byond(object):
    async def load_install(env):
        env.attr.workflow.load( {'version': env.attr.byond.install.version })
        env.attr.platform_cls = base.Byond
        env.attr.resources.compile = Shared.CountedResource(8)
        env.attr.resources.run = Shared.CountedResource(8)
        base.Byond.Install.load(env, env.attr.byond.install.version)
        await env.send_event('install.load', env)

    async def install(env):
        Byond.load_install(env)
        if not env.attr.state.get( {'action':'download'}, default=False ):
            await base.Byond.Install.download(env)
            env.attr.state.set( {'action':'download'}, True)        
