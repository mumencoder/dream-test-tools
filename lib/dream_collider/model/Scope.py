
class Scope(object):
    def __init__(self):
        self.owner = None
        self.trunk = None

        self.vars = {}
        self.procs = {}

        self.first_vars = {}
        self.first_procs = {}

    def get_usr_vars(self):
        for decl in self.vars.values():
            if not decl.stdlib:
                yield decl

    def def_var(self, name, decl):
        if name not in self.first_vars:
            self.first_vars[name] = decl
        self.vars[name] = decl

    def def_proc(self, name, decl):
        if name not in self.first_procs:
            self.first_procs[name] = decl
        self.procs[name] = decl

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
