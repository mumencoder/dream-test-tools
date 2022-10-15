
from .common import *

class Byond(object):
    def load_install(env):
        tags = {'platform':'byond', 'install.id':env.attr.install.id }
        Shared.State.open( env, **tags )
        Shared.Workflow.open( env, **tags )
        env.attr.install.platform = "byond"
        env.attr.install.dir = env.attr.byond.dirs.installs / env.attr.install.id

    async def ensure_install(env):
        if not env.attr.state(env, 'exists').get(default=False):
            await base.Byond.Install.download(env)
            env.attr.state(env, 'exists').set(True)        

    def load_runner(env):
        env.attr.workflow.open( {'runner.id':env.attr.tests.runner.id } )
        env.attr.runner.compile = base.Byond.Compilation.compile
        env.attr.runner.start_server = base.Byond.Run.run
        env.attr.resources.compile = Shared.CountedResource(8)
        env.attr.resources.run = Shared.CountedResource(8)
