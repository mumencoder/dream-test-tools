
from .common import *

from .Tests import *

class Byond(object):
    class Setup(object):
        def install(env):
            tasks = []
            tasks.append( Byond.load_install(env) )
            tasks.append( Byond.download(env).run_once() )
            env.attr.named_tasks["byond.install"] = tasks[-1]
            return Shared.Task.bounded_tasks( *tasks )

        def tests(env):
            tasks = []
            tasks.append( Tests.load_tests(env, 'default') )
            subtasks = lambda env, tenv: Shared.Task.bounded_tasks(
                Tests.tag_test( env, tenv ), 
                Tests.check_test_runnable(env),
                Tests.do_test(env)
            )
            tasks.append( Shared.Task.subtask_source(env.branch(), '.tests.all_tests', subtasks, limit=4 ) )
            return Shared.Task.bounded_tasks( *tasks )

    def load_install(env):
        def tagfn(penv, senv):
            return {'version': env.attr.byond.install.version }

        async def task(penv, senv):
            senv.attr.platform_cls = base.Byond
            base.Byond.Install.load(senv, env.attr.byond.install.version)
            Byond.config_install(senv)
        return Shared.Task( env, task, ptags={'action':'load_install'}, stags={'platform':'byond'}, tagfn=tagfn )

    def download(env):
        env = env.branch()
        async def task(penv, senv):
            await base.Byond.Install.download(senv)
        return Shared.Task( env, task, ptags={'action':'download'} )

    def config_install(env):
        env.attr.resources.compile = Shared.CountedResource(4)
        env.attr.resources.run = Shared.CountedResource(4)
