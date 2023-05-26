
from ...common import *

class TestCase(object):
    @staticmethod 
    def iter_tests(env, path):
        env = env.branch()
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.dm'):
                    env.attr.test.source_file = Shared.Path( f"{root}/{file}" )
                    yield env

    @staticmethod
    def load_test(env):
        with Shared.File.open(env.attr.test.source_file, "r") as f:
            env.attr.test.text = f.read() + '\n'
        TestCase.wrap(env)

    @staticmethod
    def wrap(env):
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

        lined_text = []
        for i, line in enumerate(env.attr.test.text.split('\n')):
            lined_text.append( f'{str(env.attr.test.line_start+i).ljust(4)}{line}')
        env.attr.test.lined_text = "\n".join(lined_text)

        text += textwrap.dedent(f"""
            /world/New()
                main()
            
                text2file("[json_encode(_log)]", "run.out")
                text2file("[json_encode(_mismatch)]", "run_unexpected.out")
                text2file("FIN", "fin")
                world.log << "shutdown()"
                shutdown()
            """)

        env.attr.test.wrapped_text = text

    @staticmethod
    def write(env):
        Shared.File.refresh(env.attr.dirs.resources / 'dmm' / 'map.dmm', env.attr.test.base_dir / 'map.dmm')
        Shared.File.refresh(env.attr.dirs.resources / 'dmf' / 'interface.dmf', env.attr.test.base_dir / 'interface.dmf')
        with Shared.File.open(env.attr.test.base_dir / 'test.dm', "w") as o:
            o.write( env.attr.test.wrapped_text  )

    @staticmethod
    def load_result(env):
        try:
            with open( env.attr.test.base_dir / 'run.out', "r") as f:
                env.attr.result.run_out = json.loads( f.read() )
        except Exception as e:
            env.attr.result.run_out = e

        try:
            with open( env.attr.test.base_dir / 'run_unexpected.out', "r") as f:
                env.attr.result.run_unexpected_out = json.loads( f.read() )
        except Exception as e:
            env.attr.result.run_unexpected_out = e
