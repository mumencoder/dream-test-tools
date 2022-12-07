
from .common import *
class TestCase(object):
    @staticmethod
    def list_all(env, input_dir):
        env = env.branch()
        env.attr.tests.dirs.root = input_dir
        for root_dir, dirnames, filenames in os.walk( input_dir ):
            for filename in filenames:
                if filename.endswith('.dm') or filename.endswith('.dme'):
                    tenv = env.branch()
                    tenv.attr.test.source_file = Shared.Path( root_dir ) / filename
                    tenv.attr.test.groups = []
                    TestCase.prepare_task(tenv)
                    yield tenv

    @staticmethod
    def prepare_task(env):
        relpath = os.path.relpath(env.attr.test.source_file.parent, env.attr.tests.dirs.root)

        if relpath != ".":
            env.attr.test.groups += relpath.split("/")

        env.attr.test.name = env.attr.test.source_file.with_suffix("").name
        env.attr.test.id = "-".join(env.attr.test.groups + [env.attr.test.name]) 
        env.attr.test.root_dir = env.attr.tests.dirs.output / env.attr.test.id

    def prepare_exec(env):
        env.attr.test.base_dir = env.attr.test.root_dir / f'{env.attr.install.platform}.{env.attr.install.id}'
        env.attr.test.files.fin = env.attr.test.base_dir / 'fin.out'
        env.attr.test.files.run_log = env.attr.test.base_dir / 'run_log.out'
        env.attr.test.files.run_unexpected = env.attr.test.base_dir / 'run_unexpected.out'

    def prepare_codetree_compile(env):
        env.attr.compilation.file_path = env.attr.test.dm_file_path
        env.attr.compilation.out = env.attr.test.base_dir / 'test.codetree'

    def prepare_compile(env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'compile.log.txt'
        env.attr.compilation.dm_file_path = env.attr.test.dm_file_path

    def prepare_run(env):
        env.attr.process.log_mode = "file"
        env.attr.process.log_path = env.attr.test.base_dir / 'run.log.txt'
        env.attr.run.dm_file_path = env.attr.platform_cls.Run.get_bytecode_file(env.attr.test.dm_file_path)
        env.attr.run.args = {'trusted':True}

    @staticmethod
    def load_test_text(env):
        with Shared.File.open(env.attr.test.source_file, "r") as f:
            env.attr.test.text = f.read() + '\n'

    @staticmethod
    def compute_lines(env):
        lined_text = []
        for i, line in enumerate(env.attr.test.text.split('\n')):
            lined_text.append( f'{str(env.attr.test.line_start+i).ljust(4)}{line}')
        env.attr.test.lined_text = "\n".join(lined_text)

    @staticmethod
    def wrap(env):
        TestCase.load_test_text(env)

        text = textwrap.dedent(f"""                    
            #include "map.dmm"
            #include "interface.dmf"

            var/list/_log = new
            var/list/_multilog = new
            var/list/_mismatch = new

            /proc/_LOGADD(name, value)
                if (name in _log)
                    if (name in _multilog)
                        _log[name] += value
                    else
                        _multilog[name] = 1
                        _log[name] = list( _log[name], value )
                else
                    _log[name] = value

            /proc/EXPECT(name, actual, expected)
                if (actual ~= expected) 
                    _LOGADD("expected", actual)
                else
                    _mismatch[name] = list(actual, expected)

            /proc/LOG(arg1, arg2)
                var/name
                var/value
                if (isnull(arg2))
                    name = "log"
                    value = arg1
                else
                    name = arg1
                    value = arg2
                _LOGADD(name, value)
        """)

        env.attr.test.line_start = len(text.split('\n'))
        text += env.attr.test.text
        TestCase.compute_lines(env)

        text += textwrap.dedent(f"""
            /world/New()
                main()
            
                fdel("{env.attr.test.files.run_log }")
                fdel("{env.attr.test.files.run_unexpected}")
                fdel("{env.attr.test.files.fin}")
                text2file("[json_encode(_log)]", "{env.attr.test.files.run_log }")
                text2file("[json_encode(_mismatch)]", "{env.attr.test.files.run_unexpected}")
                text2file("FIN", "{env.attr.test.files.fin}")
                world.log << "shutdown()"
                //shutdown()
            """)

        env.attr.test.wrapped_text = text

    @staticmethod
    def write(env):
        env.attr.test.dm_file_path = env.attr.test.base_dir / 'test.dm' 
        Shared.File.refresh(env.attr.tests.dirs.resources / 'map.dmm', env.attr.test.base_dir / 'map.dmm')
        Shared.File.refresh(env.attr.tests.dirs.resources / 'interface.dmf', env.attr.test.base_dir / 'interface.dmf')
        with Shared.File.open(env.attr.test.dm_file_path, "w") as o:
            o.write( env.attr.test.wrapped_text  )