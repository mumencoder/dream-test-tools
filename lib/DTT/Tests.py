
from .common import *

class TestsApp(object):
    def prepare_compile(self, env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'compile.log.txt'
        env.attr.compilation.dm_file_path = env.attr.test.dm_file_path
        env.attr.compilation.args = {}

    def prepare_run(self, env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'run.log.txt'
        env.attr.run.dm_file_path = env.attr.platform_cls.Run.get_bytecode_file(env.attr.test.dm_file_path)
        env.attr.run.args = {'trusted':True}
        env.event_handlers['process.wait'] = self.wait_run_complete

    async def prepare_build(self, env):
        await Shared.Path.sync_folders( env, env.attr.source.dir, env.attr.install.dir )
        env.attr.dotnet.solution.path = env.attr.install.dir

    async def wait_run_complete(self, env):
        process = env.attr.process.p
        fin_path = env.attr.test.base_dir / 'fin.out'
        while process.returncode is None:
            if os.path.exists(fin_path):
                if os.stat(fin_path).st_mtime > env.attr.process.start_time:
                    try:
                        process.kill()
                        await asyncio.wait_for(process.wait(), timeout=2.0)
                    except asyncio.exceptions.TimeoutError:
                        pass
            try:
                await asyncio.wait_for(process.wait(), timeout=0.10)
            except asyncio.exceptions.TimeoutError:
                pass

    def prepare_codetree_compile(self):
        env.attr.compilation.file_path = env.attr.test.dm_file_path
        env.attr.compilation.out = env.attr.test.base_dir / 'test.codetree'

    def load_test_tasks(self, env):
        for tenv in TestCase.list_all(env, env.attr.tests.dirs.dm_files):
            yield self.do_test_task(tenv)
            
    def do_test_task(self, env):
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
            self.prepare_compile(compile_env)
            await env.attr.platform_cls.Compilation.compile(compile_env)

            with Shared.File.open(compile_env.attr.test.base_dir / "compile.returncode.log", "w") as o:
                o.write( str(compile_env.attr.compilation.returncode) )

            if compile_env.attr.compilation.returncode == 0:
                run_env = senv.branch()
                self.prepare_run(run_env)
                await env.attr.platform_cls.Run.run(run_env)
        return Shared.Task(env, task, tags={'test_id':env.attr.test.id})