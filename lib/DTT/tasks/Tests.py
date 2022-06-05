
from .common import *

from .TestCase import *

class Tests(object):
    def run_tests(env, tenvs):
        async def create_task(penv, senv):
            tasks = []
            for tenv in tenvs:
                t = Tests.do_test(tenv)
                Shared.Task.link(t1, t)
                tasks.append(t)
            
            if len(tasks) > 0:
                bottom = Shared.Task.meet( senv, "do_tests", Shared.Task.link_exec, tasks )
                bottom.initialize(senv)
                Shared.Task.link_exec(bottom, t2)

        async def save_task(penv, senv):
            senv.attr.state.results.set(f'{senv.attr.tests.tag}.tests.completed', list(senv.attr.tests.completed))
            await senv.send_event('tests.completed', senv)

        t1 = Shared.Task(env, create_task, tags={'action':'create_task'} )
        t2 = Shared.Task(env, save_task, tags={'action':'save_task'} )
        Shared.Task.link(t1, t2)
        return Shared.TaskBound(t1, t2)

    def run_incomplete_tests(env):
        async def task(penv, senv):
            Shared.Task.link( penv.attr.self_task, Tests.run_tests(env, senv.attr.tests.incomplete) )
        return Shared.Task(env, task, tags={'action':'run_incomplete_tests'} )

    def clear_tests(env, tests_tag):
        async def task(penv, senv):
            senv.attr.tests.tag = f'{senv.attr.install.tag}.{tests_tag}'
            senv.attr.state.results.rm(f'{senv.attr.tests.tag}.tests.completed')
        return Shared.Task(env, task, tags={'action':'clear_tests'})

    def load_incomplete_tests(env, tests_tag):
        async def task(penv, senv):
            senv.attr.tests.tag = f'{senv.attr.install.tag}.{tests_tag}'
            senv.attr.tests.completed = set(senv.attr.state.results.get(f'{senv.attr.tests.tag}.tests.completed', default=[]))
            incomplete_tests = set()
            for tenv in TestCase.list_all(env, env.attr.tests.dirs.dm_files):
                if tenv.attr.test.id in senv.attr.tests.completed:
                    continue
                incomplete_tests.add( tenv )
            senv.attr.tests.incomplete = incomplete_tests

        return Shared.Task(env, task, tags={'action':'load_incomplete_tests'})
                
    def prepare_compile(env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'compile.log.txt'
        env.attr.compilation.dm_file_path = env.attr.test.dm_file_path
        env.attr.compilation.args = {}

    def prepare_run(env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'run.log.txt'
        env.attr.run.dm_file_path = env.attr.platform_cls.Run.get_bytecode_file(env.attr.test.dm_file_path)
        env.attr.run.args = {'trusted':True}
        env.event_handlers['process.wait'] = Tests.wait_run_complete

    def do_test(env):
        env = env.branch()
        Shared.Task.tags(env, {'action':'do_test'} )
        async def task(penv, senv):
            penv.merge(senv, inplace=True)

            TestCase.prepare_exec(penv)
            penv.attr.test.files.fin = penv.attr.test.base_dir / 'fin.out'
            penv.attr.test.files.run_log = penv.attr.test.base_dir / 'run_log.out'
            penv.attr.test.files.run_unexpected = penv.attr.test.base_dir / 'run_unexpected.out'
            TestCase.wrap(penv)
            TestCase.write(penv)
            senv.merge(penv, inplace=True)

            compile_env = senv.branch()
            Tests.prepare_compile(compile_env)
            await senv.attr.platform_cls.Compilation.compile(compile_env)

            with Shared.File.open(compile_env.attr.test.base_dir / "compile.returncode.log", "w") as o:
                o.write( str(compile_env.attr.compilation.returncode) )

            if compile_env.attr.compilation.returncode == 0:
                run_env = senv.branch()
                Tests.prepare_run(run_env)
                await senv.attr.platform_cls.Run.run(run_env)

            senv.attr.tests.completed.add(senv.attr.test.id)

        return Shared.Task(env, task, tags={'test_id':env.attr.test.id})

    async def wait_run_complete(env):
        process = env.attr.process.p
        fin_path = env.attr.test.base_dir / 'fin.out'
        start_time = time.time()
        kill_proc = False
        while process.returncode is None:
            if time.time() - start_time > 20:
                kill_proc = True
            if os.path.exists(fin_path):
                if os.stat(fin_path).st_mtime > env.attr.process.start_time:
                    kill_proc = True
            if kill_proc:
                try:
                    process.kill()
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except asyncio.exceptions.TimeoutError:
                    pass
            try:
                await asyncio.wait_for(process.wait(), timeout=0.10)
            except asyncio.exceptions.TimeoutError:
                pass

    def prepare_codetree_compile(env):
        env.attr.compilation.file_path = env.attr.test.dm_file_path
        env.attr.compilation.out = env.attr.test.base_dir / 'test.codetree'
