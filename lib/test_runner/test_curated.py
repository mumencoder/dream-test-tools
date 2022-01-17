
import os

import Shared

def list_all_tests(base_config, input_dir):
    for root_dir, dirnames, filenames in os.walk( input_dir ):
        for filename in filenames:
            if filename.endswith('.dm') or filename.endswith('.dme'):
                config = base_config.branch('test')
                config['test.source_file'] = Shared.Path( root_dir ) / filename
                yield config