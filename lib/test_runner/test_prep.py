
import os
import Shared

### tests
def wrap_test(config, test_text):
    text = f"""

#include "map.dmm"
#include "interface.dmf"

var/list/_log = new
var/list/_mismatch = new

/proc/LOG(name, value, expected = null)
    if (!isnull(expected))
        if (value != expected) 
            _mismatch[name] = list(value, expected)
    else
        _log[name] = value

{test_text} 

/world/New()
    main()

    text2file("[json_encode(_log)]", "_log.{config['test.platform']}.out")
    text2file("[json_encode(_mismatch)]", "_mismatch.{config['test.platform']}.out")
    text2file("FIN", "fin.{config['test.platform']}.out")
    shutdown()
"""

    return text

def setup_test(config):
    Shared.File.refresh(config['tests_dir.resources'] / 'map.dmm', config['test.base_dir'] / 'map.dmm')
    Shared.File.refresh(config['tests_dir.resources'] / 'interface.dmf', config['test.base_dir'] / 'interface.dmf')

async def all_fixed_tests(config, input_dir, output_dir, test_consumer):
    for root_dir, dirnames, filenames in os.walk( input_dir ):
        for filename in filenames:
            src_dm_file = Shared.Path( root_dir ) / filename
            test_config, single_fixed_test(config, root_dir, src_dm_file, output_dir)
            await test_consumer(test_config)

async def single_fixed_test(config, root_dir, src_dm_file, output_dir):
    test_config = config.branch('single_fixed_test')
    relpath = os.path.relpath(src_dm_file.parent, root_dir).split("/")
    test_config['test.id'] = "fixed-" + "-".join( relpath ) + "-" + src_dm_file.with_suffix("").name
    test_config['test.base_dir'] = output_dir / 'single_tests' / test_config['test.id']
    test_config['test.dm_file_path'] = test_config['test.base_dir'] / os.path.basename(src_dm_file)
    test_config['test.filename'] = os.path.basename(test_config['test.dm_file_path'])

    with open(src_dm_file, "r") as f:
        test_text = wrap_test( test_config, f.read() ) + '\n'
    with open(test_config['test.dm_file_path'], "w") as f:
        f.write( test_text )

    setup_test(test_config)

    return test_config

async def write_test(config, test_text):
    test_config = config.branch('write_test')
    test_config['test.dm_file_path'] = test_config['test.base_dir'] / 'test.dm'
    with open(test_config['test.dm_file_path'] , "w") as o:
        o.write( test_text )
    setup_test(test_config)
    return test_config
