
import os

import Shared

def list_all_tests(base_env, input_dir):
    env2 = base_env.branch()
    env2.attr.tests.dirs.root = input_dir
    for root_dir, dirnames, filenames in os.walk( input_dir ):
        for filename in filenames:
            if filename != "hello_world.dm" and base_env.attr.test_mode == "quick":
                continue
            if filename.endswith('.dm') or filename.endswith('.dme'):
                env = env2.branch()
                env.attr.test.source_file = Shared.Path( root_dir ) / filename
                yield env