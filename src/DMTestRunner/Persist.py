
from .common import *

class Persist:
    def is_generated(env):
        if env.attr_exists('.test.metadata.paths.dm_file'):
            return True
        else:
            return False

    def load_test(env):
        env.attr.test.metadata_path = env.attr.test.root_dir / 'test.metadata.json'
        if os.path.exists( env.attr.test.metadata_path ):
            with open(env.attr.test.metadata_path, "r") as f:
                md = json.load(f)
                for attr, value in md.items():
                    env.properties[attr] = value

    def save_test(env):
        env.attr.test.metadata_path = env.attr.test.root_dir / 'test.metadata.json'

        md = {}
        for attr in env.unique_properties():
            if attr.startswith( '.test.metadata.' ):
                md[attr] = env.get_attr(attr)

        with open( env.attr.test.metadata_path, "w" ) as f:
            f.write( json.dumps(md) )
                
    def try_init_test_instance(env):
        env.attr.test.metadata.name = Shared.Random.generate_string(24)
        env.attr.test.root_dir = env.attr.tests.root_dir / env.attr.test.metadata.name
        Persist.load_test(env)

    def save_test_dm(tenv):
        tenv.attr.test.metadata.paths.dm_file = 'test.dm'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.dm_file, "w") as f:
            f.write( tenv.attr.collider.builder.text )

    def save_test_ngrams(tenv):
        tenv.attr.test.metadata.paths.ngram_info = 'ngram_info.json'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.ngram_info, "w") as f:
            f.write( json.dumps( tenv.attr.collider.builder.ngram_info ) )

    def save_collider_info(tenv):
        tenv.attr.test.metadata.paths.collider_ast = 'collider_ast.txt'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_ast, "w") as f:
            s = io.StringIO()
            tenv.attr.collider.builder.print(s)
            f.write( s.getvalue() )

        tenv.attr.test.metadata.paths.collider_model = 'collider_model.json'
        with open( tenv.attr.test.root_dir / tenv.attr.test.metadata.paths.collider_model, "w") as f:
            f.write( json.dumps(tenv.attr.collider.builder.get_model(), cls=DreamCollider.ModelEncoder) )

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
