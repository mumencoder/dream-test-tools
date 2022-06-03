

import os
import textwrap
import Shared

class TestCase(object):
    @staticmethod
    def list_all(base_env, input_dir):
        env2 = base_env.branch()
        env2.attr.tests.dirs.root = input_dir
        for root_dir, dirnames, filenames in os.walk( input_dir ):
            for filename in filenames:
                if filename.endswith('.dm') or filename.endswith('.dme'):
                    tenv = env2.branch()
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

    @staticmethod
    def load_test_text(env):
        with Shared.File.open(env.attr.test.source_file, "r") as f:
            env.attr.test.text = f.read() + '\n'

    @staticmethod
    def wrap(env):
        TestCase.load_test_text(env)

        text = textwrap.dedent(f"""                    
            #include "map.dmm"
            #include "interface.dmf"

            var/list/_log = new
            var/list/_mismatch = new

            /proc/LOG(name, value, expected = null)
                if (!isnull(expected))
                    if (value ~= expected) 
                        _log[name] = value
                    else
                        _mismatch[name] = list(value, expected)
                else
                    _log[name] = value""")

        text += env.attr.test.text

        text += textwrap.dedent(f"""
            /world/New()
                main()
            
                fdel("{env.attr.test.files.run_log }")
                fdel("{env.attr.test.files.run_unexpected}")
                fdel("{env.attr.test.files.fin}")
                text2file("[json_encode(_log)]", "{env.attr.test.files.run_log }")
                text2file("[json_encode(_mismatch)]", "{env.attr.test.files.run_unexpected}")
                text2file("FIN", "{env.attr.test.files.fin}")
                shutdown()
            """)

        env.attr.test.wrapped_text = text

    @staticmethod
    def write(env):
        env.attr.test.dm_file_path = env.attr.test.base_dir / 'test.dm' 
        Shared.File.refresh(env.attr.tests.dirs.resources / 'map.dmm', env.attr.test.base_dir / 'map.dmm')
        Shared.File.refresh(env.attr.tests.dirs.resources / 'interface.dmf', env.attr.test.base_dir / 'interface.dmf')
        with Shared.File.open(env.attr.test.dm_file_path, "w") as o:
            o.write( env.attr.test.wrapped_text  )