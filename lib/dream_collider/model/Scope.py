
class Scope(object):
    def __init__(self):
        self.vars = {}
        self.values = {}
        self.procs = {}

    def find_name(self, name):
        dmobj = self.obj_tree.get_object( self.scope )
        while dmobj is not None:
            v = self.values.get( (str(dmobj.path), ident) )
            if v is not None:
                return v
            dmobj = dmobj.obj_trunk
        return None
        
    def set_value(self, name, value):
        self.values[ name ] = value

    def get_value(self, name):
        scope = self.find_name(name)
