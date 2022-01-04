
class Scope(object):
    def __init__(self):
        self.owner = None
        self.trunk = None

        self.vars = {}
        self.values = {}
        self.procs = {}

    def find_var(self, name):
        scope = self
        while scope is not None:
            if name in self.vars:
                return scope
            scope = scope.trunk
        return None

    def find_proc(self, name):
        scope = self
        while scope is not None:
            if name in self.procs:
                return scope
            scope = scope.trunk
        return None

    def set_value(self, name, value):
        self.values[ name ] = value

    def get_value(self, name):
        scope = self.find_var(name)
        if scope is None:
            return None
        return scope.values[ name ]