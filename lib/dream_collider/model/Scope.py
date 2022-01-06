
class Scope(object):
    def __init__(self):
        self.owner = None
        self.trunk = None

        self.vars = {}
        self.procs = {}

        self.values = {}

    def get_usr_vars(self):
        for decl in self.vars.values():
            if not decl.stdlib:
                yield decl
                
    def find_var(self, name):
        scope = self
        while scope is not None:
            if name in scope.vars:
                return scope
            scope = scope.trunk
        return None

    def find_proc(self, name):
        scope = self
        while scope is not None:
            if name in scope.procs:
                return scope
            scope = scope.trunk
        return None

    def set_value(self, name, value):
        self.values[ name ] = value

    def get_value(self, name):
        scope = self
        while scope is not None:
            if name in scope.values:
                return scope.values[ name ]
            scope = scope.trunk
        return None
