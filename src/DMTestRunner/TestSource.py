
class TestSource:
    @staticmethod
    def from_directory(env):
        env = env.branch()
        env.attr.tests.root_dir = input_dir
        for root_dir, dirnames, filenames in os.walk( input_dir ):
            for filename in filenames:
                if filename.endswith('.dm') or filename.endswith('.dme'):
                    tenv = env.branch()
                    tenv.attr.test.source_file = Shared.Path( root_dir ) / filename
                    tenv.attr.test.groups = []
                    TestCase.prepare_task(tenv)
                    yield tenv