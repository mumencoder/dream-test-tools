
from .common import *

from .TestCase import *

class Tests(object):
    def get_tag(env):
        env.attr.tests.runner.tag = f'{env.attr.tests.runner.id}.{tests_tag}'

    def load_tests(env):
        env.attr.tests.all_tests = list(TestCase.list_all(env, env.attr.tests.dirs.dm_files))

    def check_complete_tests(env):
        env.attr.state.get(env, '.tests.completed', default=[])
        env.attr.tests.incomplete = set()
        redo_tests = env.get_attr( '.tests.config.redo_tests', default=[])
        for tenv in env.attr.tests.all_tests:
            if tenv.attr.test.id not in env.attr.tests.completed:
                env.attr.tests.incomplete.add( tenv.attr.test.id )
            else:
                for redo_test_name in redo_tests:
                    if redo_test_name in tenv.attr.test.id:
                        env.attr.tests.incomplete.add( tenv.attr.test.id )
                        env.attr.tests.completed.remove( tenv.attr.test.id )

    def run_tests(env):
        await Shared.Task.subtask_source(env, '.tests.incomplete', do_test, limit=32, tags={'action':'run_tests'} )
        env.attr.task.log(f"incomplete {len(env.attr.tests.incomplete)} {env.attr.tests.incomplete}")
        env.attr.task.log(f"complete {len(env.attr.tests.completed)} {env.attr.tests.completed}")
        env.attr.state.set(f'.tests.completed', list(env.attr.tests.completed))
        await env.send_event('tests.completed', env)

    def do_test(env):
        env.attr.workflow.open({'test_id':tenv.attr.test.id})
        env.merge(env.attr.tests.tenv, inplace=True)

        TestCase.prepare_exec(env)
        TestCase.wrap(env)
        TestCase.write(env)

        compile_env = env.branch()
        Tests.prepare_compile(compile_env)
        await env.attr.platform_cls.Compilation.compile(compile_env)

        with Shared.File.open(compile_env.attr.test.base_dir / "compile.returncode.log", "w") as o:
            o.write( str(compile_env.attr.compilation.returncode) )

        if compile_env.attr.compilation.returncode == 0:
            run_env = env.branch()
            Tests.prepare_run(run_env)
            await env.attr.platform_cls.Run.run(run_env)

        env.attr.tests.completed.add(env.attr.test.id)
        await env.send_event('test.complete', env)

    def clear_tests(env):
        senv.attr.state.rm(f'.tests.completed')

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
