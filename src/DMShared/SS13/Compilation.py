

from ..common import *

class Compilation(object):
    @staticmethod
    def is_dme(name):
        return name.split('.')[-1] == 'dme'

    @staticmethod
    def find_dme(env):
        base_dir = env.attr.compilation.root_dir
        if not os.path.exists(base_dir):
            raise Exception("DME directory does not exist")
            
        dme_list = [entry for entry in os.listdir(base_dir) if Compilation.is_dme(entry)]
        if len(dme_list) == 1:
            env.attr.compilation.dm_file_path = base_dir / dme_list[0]
        else:
            env.attr.compilation.dm_file_path = None    