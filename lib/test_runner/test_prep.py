
import os
import Shared


### tests
class TestWrapper(object):
    def __init__(self, config, test_text):
        self.test_text = test_text
        self.files = {}

    def wrapped_test(self, config):
        self.files["log"] = f"run_log.out"
        self.files["mismatch"] = f"run_unexpected.out"
        self.files["fin"] = f"fin.out"
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

def load_install(config, install):
    install["id"] = f"{install['platform']}.{install['install_id']}"
    return install

def get_test_info(config, folder_name):
    relpath = os.path.relpath(config['test.source_file'].parent, config['tests.dirs.input']).split("/")
    config['test.id'] = "curation-" + "-".join( relpath ) + "-" + config['test.source_file'] .with_suffix("").name
    config['test.base_dir'] = config['tests.dirs.output'] / folder_name / config['test.id'] / config["test.install"]["id"]
    with open(config['test.source_file'], "r") as f:
        config['test.text'] = f.read() + '\n'

def copy_test(config):
    config['test.dm_file_path'] = config['test.base_dir'] / 'test.dm'
    Shared.File.refresh(config['tests.dirs.resources'] / 'map.dmm', config['test.base_dir'] / 'map.dmm')
    Shared.File.refresh(config['tests.dirs.resources'] / 'interface.dmf', config['test.base_dir'] / 'interface.dmf')
    final_text = TestWrapper(config, config['test.text']).wrapped_test(config)
    with open(config['test.dm_file_path'], "w") as o:
        o.write( final_text )