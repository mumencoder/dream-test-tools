
import os

import Shared

def list_all_tests(config, input_dir):
    for root_dir, dirnames, filenames in os.walk( input_dir ):
        for filename in filenames:
            if filename.endswith('.dm') or filename.endswith('.dme'):
                src_dm_file = Shared.Path( root_dir ) / filename
                yield src_dm_file

def read_single_test(config, root_dir, src_dm_file, output_dir):
    relpath = os.path.relpath(src_dm_file.parent, root_dir).split("/")
    config['test.id'] = "curation-" + "-".join( relpath ) + "-" + src_dm_file.with_suffix("").name
    config['test.base_dir'] = output_dir / 'curated' / config['test.id'] / f"{config['test.platform']}.{config['test.install_id']}"
    config['test.dm_file_path'] = config['test.base_dir'] / os.path.basename(src_dm_file)
    config['test.filename'] = os.path.basename(config['test.dm_file_path'])

    with open(src_dm_file, "r") as f:
        config['test.text'] = f.read() + '\n'