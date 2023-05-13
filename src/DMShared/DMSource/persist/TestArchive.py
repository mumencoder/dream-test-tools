
from ...common import *

class TestArchive:
    def load(env, data):
        if "clear_on_load" in data:
            if type(data["clear_on_load"]) is not bool:
                raise Exception("expected bool for clear_on_load") 
            if os.path.exists( data["path"] ) and data["clear_on_load"]:
                shutil.rmtree( data["path"] )
        env.attr.tests.root_dir = Shared.Path( data["path"] )

    def try_init_test_instance(env):
        env.attr.test.metadata.name = Shared.Random.generate_string(24)
        env.attr.test.root_dir = env.attr.tests.root_dir / env.attr.test.metadata.name
        Persist.load_test(env)
        
    def iter_tests(root_env):
        for path, dirs, files in os.walk(root_env.attr.tests.root_dir):
            tenv = root_env.branch()
            tenv.attr.test.root_dir = Shared.Path( path )
            Metadata.load_test(tenv)
            if tenv.has_attr('.test.metadata.name'):
                yield tenv

    def iter_existing_tests(env):
        for path, dirs, files in os.walk(env.attr.tests.root_dir):
            tenv = env.branch()
            tenv.attr.test.root_dir = Shared.Path( path )
            Persist.load_test(tenv)
            if Persist.is_generated(tenv):
                yield tenv

    def clean_tests(tests_dir, known_tests):
        cleaned = 0
        start_time = time.time()
        for test_dir in os.listdir(tests_dir):
            if test_dir not in known_tests:
                shutil.rmtree( tests_dir / test_dir )
                cleaned += 1
        print(f"cleaned {cleaned} tests in {time.time()-start_time}")