
from .common import *

class ByondApp(object):
    def byond_tasks(self, env):

        env.attr.platform_cls = Byond

        t_load_byond = self.load_byond_task(env, self.byond_ref_version)
        tg = Shared.TaskGraph( "byond_tasks", env, t_load_byond )

        t_install = self.download_byond_task(env)
        t_install.run_once( )
        tg.link( t_load_byond, t_install )

        Shared.Task.split( tg, t_install, *self.load_test_tasks(env) )

        #print( tg.dag.stringify() )
        return tg

    def load_byond_task(self, env, version):
        Shared.Task.tags(env, {'platform':'byond', 'version':version} )
        async def task(penv, senv):
            Byond.Install.load(senv, version)
            senv.attr.tasks.base_tags = {'install':senv.attr.install.id}
            senv.attr.byond.install.version = version
            print( senv.attr.install.id )
        return Shared.Task( env, task )

    def download_byond_task(self, env):
        env = env.branch()
        Shared.Task.tags(env, {'action':'download'} )
        async def task(penv, senv):
            await Byond.Install.download(senv)
            print( senv.attr.install.id )
        return Shared.Task( env, task )




