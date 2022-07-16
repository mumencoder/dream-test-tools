
from .common import *

from .TestCase import *

class Tests(object):
    def load_tests(env, tests_tag):
        async def task(penv, senv):
            senv.attr.tests.tag = f'{senv.attr.install.id}.{tests_tag}'
            senv.attr.tests.completed = set(senv.attr.state.results.get(f'{senv.attr.tests.tag}.tests.completed', default=[]))
            senv.attr.tests.all_tests = list(TestCase.list_all(env, env.attr.tests.dirs.dm_files))
            senv.attr.tests.incomplete = set()
            redo_tests = senv.get_attr( '.config.redo_tests', default=[])
            for tenv in senv.attr.tests.all_tests:
                if tenv.attr.test.id not in senv.attr.tests.completed:
                    senv.attr.tests.incomplete.add( tenv.attr.test.id )
                else:
                    for redo_test_name in redo_tests:
                        if redo_test_name in tenv.attr.test.id:
                            senv.attr.tests.incomplete.add( tenv.attr.test.id )
                            senv.attr.tests.completed.remove( tenv.attr.test.id )

        return Shared.Task(env, task, ptags={'action':'load_incomplete_tests'})

    def run_tests(env):
        subtasks = lambda penv, senv, tenv: Shared.Task.bounded_tasks(
            Tests.tag_test( env, tenv.branch() ), 
            Tests.check_test_runnable(env),
            Tests.do_test(env)
        )
        return Shared.Task.subtask_source(env, '.tests.all_tests', subtasks, limit=32, tags={'action':'run_tests'} )

    def tag_test(env, tenv):
        async def task(penv, senv):
            senv.attr.tests.tenv = tenv
            senv.merge(senv.attr.tests.tenv, inplace=True)
        return Shared.Task(env, task, ptags={'action':'tag_test'}, stags={'test_id':tenv.attr.test.id})

    def check_test_runnable(env):
        async def task(penv, senv):
            halt = False
            if senv.attr.test.id in senv.attr.tests.completed:
                halt = True
            if halt is True:
                penv.attr.self_task.halt()
        return Shared.Task(env, task, ptags={'action':'check_test_runnable'})

    def do_test(env):
        async def task(penv, senv):
            TestCase.prepare_exec(senv)
            TestCase.wrap(senv)
            TestCase.write(senv)

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
            await senv.send_event('test.complete', senv)

        return Shared.Task(env, task, {'action':'do_test'})

    def save_complete_tests(env):
        async def task(penv, senv):
            penv.attr.self_task.log(f"incomplete {len(senv.attr.tests.incomplete)} {senv.attr.tests.incomplete}")
            penv.attr.self_task.log(f"complete {len(senv.attr.tests.completed)} {senv.attr.tests.completed}")
            senv.attr.state.results.set(f'{senv.attr.tests.tag}.tests.completed', list(senv.attr.tests.completed))
            await senv.send_event('tests.completed', senv)
        return Shared.Task(env, task, {'action':'save_complete_tests'})

    def clear_tests(env, tests_tag):
        async def task(penv, senv):
            senv.attr.state.results.rm(f'{senv.attr.install.id}.{tests_tag}.tests.completed')
        return Shared.Task(env, task, ptags={'action':'clear_tests'})

    def prepare_compile(env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'compile.log.txt'
        env.attr.compilation.dm_file_path = env.attr.test.dm_file_path

    def prepare_run(env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'run.log.txt'
        env.attr.run.dm_file_path = env.attr.platform_cls.Run.get_bytecode_file(env.attr.test.dm_file_path)
        env.attr.run.args = {'trusted':True}
        env.event_handlers['process.wait'] = Tests.wait_run_complete

    async def wait_run_complete(env):
        process = env.attr.process.p
        fin_path = env.attr.test.base_dir / 'fin.out'
        start_time = time.time()
        kill_proc = False
        while process.returncode is None:
            if time.time() - start_time > 30:
                kill_proc = True
            if os.path.exists(fin_path):
                if os.stat(fin_path).st_mtime > env.attr.process.start_time:
                    kill_proc = True
            if kill_proc:
                try:
                    process.kill()
                    #process.send_signal(signal.SIGKILL)
                    #os.system(f"kill -9 {process.pid}")
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
