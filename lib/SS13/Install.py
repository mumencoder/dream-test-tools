
import os

class Install(object):
    @staticmethod
    def is_dme(name):
        return name.split('.')[-1] == 'dme'

    @staticmethod
    def find_dme(config):
        if not os.path.exists(config['ss13.base_dir']):
            return
            
        dme_list = [entry for entry in os.listdir(config['ss13.base_dir']) if Install.is_dme(entry)]
        if len(dme_list) == 1:
            config['ss13.dme_file'] = os.path.join(config['ss13.base_dir'], dme_list[0])
        else:
            config['ss13.dme_file'] = None

    def dme_from_testgame(config, build):
        yield {"name":'testgame', 'dme': build.solution_dir / 'TestGame' / 'code.dm'}

