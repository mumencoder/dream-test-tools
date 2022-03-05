
import os
import Shared

class TestWrapper(object):
    def __init__(self, test_text):
        self.test_text = test_text
        self.files = {}

    def wrapped_test(self):
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

def generate_test(env):
    env.attr.test.dm_file_path = env.attr.test.base_dir / 'test.dm' 
    Shared.File.refresh(env.attr.tests.dirs.resources / 'map.dmm', env.attr.test.base_dir / 'map.dmm')
    Shared.File.refresh(env.attr.tests.dirs.resources / 'interface.dmf', env.attr.test.base_dir / 'interface.dmf')
    final_text = TestWrapper(env.attr.test.text).wrapped_test()
    with open(env.attr.test.dm_file_path, "w") as o:
        o.write( final_text )