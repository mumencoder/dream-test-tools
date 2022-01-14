
import os
import Shared


### tests
class TestWrapper(object):
    def __init__(self, config, test_text):
        self.test_text = test_text
        self.files = {}

    def wrapped_test(self, config):
        self.files["log"] = f"{config['test.platform']}.run_log.out"
        self.files["mismatch"] = f"{config['test.platform']}.run_unexpected.out"
        self.files["fin"] = f"{config['test.platform']}.fin.out"
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

{self.test_text} 

/world/New()
    main()

    fdel("{self.files["log"]}")
    fdel("{self.files["mismatch"]}")
    fdel("{self.files["fin"]}")
    text2file("[json_encode(_log)]", "{self.files["log"]}")
    text2file("[json_encode(_mismatch)]", "{self.files["mismatch"]}")
    text2file("FIN", "{self.files["fin"]}")
    shutdown()
"""

        return text

def copy_resources(config):
    Shared.File.refresh(config['tests_dir.resources'] / 'map.dmm', config['test.base_dir'] / 'map.dmm')
    Shared.File.refresh(config['tests_dir.resources'] / 'interface.dmf', config['test.base_dir'] / 'interface.dmf')

async def write_test(config, test_text):
    config['test.dm_file_path'] = config['test.base_dir'] / 'test.dm'
    with open(config['test.dm_file_path'], "w") as o:
        o.write( test_text )
    copy_resources(config)