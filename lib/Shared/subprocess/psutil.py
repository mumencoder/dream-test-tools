
import psutil

class Psutil(object):
    @staticmethod
    def find(name=None, env_tag=None):
        pinfos = []
        scan_items = []
        if name is not None:
            scan_items.append('name')
        if env_tag is not None:
            scan_items.append('environ')

        for p_update in psutil.process_iter(['name']):
            if name is not None and p_update.name() == name:
                pinfos.append( p_update )
            elif env_tag is not None:
                try:
                    env = p_update.environ()
                    k, v = env_tag
                    if k in env and env[k] == v:
                        pinfos.append( p_update ) 
                except psutil.AccessDenied:
                    pass
        return pinfos

    @staticmethod
    def find_by_tag(tag):
        return Psutil.find( env_tag=('process_tag', tag))
