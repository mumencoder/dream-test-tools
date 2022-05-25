
from .common import *

class ClopenDreamApp(object):
    async def parse_clopendream_tests(self):
        clenv = self.env.branch()
        ClopenDream.Source.load(clenv, 'main')
        clenv.attr.clopendream.source.location = 'https://github.com/mumencoder/Clopendream-parser'
        ClopenDream.Install.load(clenv, 'main')

        for tenv in test_runner.list_all_tests(clenv, self.env.attr.tests.dirs.dm_files):
            
            test_runner.Curated.load_test( tenv )
            test_runner.Curated.prepare_test( tenv )
            test_runner.generate_test( tenv )

            tenv.attr.byond.compilation.file_path = tenv.attr.test.dm_file_path
            tenv.attr.clopendream.install.working_dir = tenv.attr.test.base_dir

            Shared.TaskGraph.Build.open(tenv, f"clopendream.test.{tenv.attr.test.id}")
            Shared.Workflow.set_task(tenv, self.parse_clopendream_test(tenv, 'currentdev') )

        await Shared.Workflow.run_all(self.env)

    async def parse_clopendream_test(self, tenv, clopen_id):
        btenv, ctenv = self.prepare_parse_clopendream_test(tenv, clopen_id)
        test_runner.Curated.prepare_test( btenv )
        test_runner.generate_test( btenv )
        await Byond.Compilation.generate_code_tree(btenv)

        await ClopenDream.Install.parse(ctenv)

    async def prepare_empty(env):
        empty_dir = env.attr.dirs.state / 'empty'
        with Shared.File.open(env.attr.dirs.state / 'empty' / 'empty.dm', "w") as f:
            f.write('\n')

        benv = env.branch()
        Byond.Install.load(benv, 'main')
        benv.attr.byond.compilation.file_path = empty_dir / 'empty.dm'
        benv.attr.byond.compilation.out = empty_dir / 'empty.codetree'
        await Byond.Compilation.generate_code_tree(benv)

    async def build_clopendream(base_env):
        env = base_env.branch()
        await ClopenDream.Builder.build(env)
        Shared.Path.sync_folders( env, env.attr.clopendream.source.dir, env.attr.clopendream.install.dir )
        ClopenDream.Install.copy_stdlib(env)

    async def prepare_parse_clopendream_test(tenv, clopen_id):
        btenv = tenv.branch()
        Byond.Install.load(btenv, 'main')
        test_runner.Curated.load_test( btenv )
        btenv.attr.byond.compilation.out = btenv.attr.test.base_dir / 'test.codetree'

        ctenv = tenv.branch()
        ClopenDream.Install.load(ctenv, clopen_id)
        ctenv.attr.byond.codetree = btenv.attr.byond.compilation.out
        yield btenv, ctenv