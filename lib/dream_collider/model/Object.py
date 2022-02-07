
import random 

from ..common import *
from ..model import *

class ObjectVarDecl(object):
    def __init__(self):
        self.path = None
        self.name = None
        self.flags = []
        self.initial = None
        self.value = None

        self.stdlib = False
        self.allow_override = True

    def __str__(self):
        if self.stdlib is True:
            return ""
            
        if len(self.path.segments) != 0:
            path = str(self.path) + '/'
        else:
            path = ""
        if not self.is_override:
            path += 'var/'
        for flag in self.flags:
            path += flag + '/'
        path += self.name
        return path + ' = ' + str(self.initial)

    def pick_random_previous_decl(self, config):
        if random.random() < 0.02:
            return self
        else:
            return self.prev_decl.pick_random_previous_decl(config)

    def initialization_mode(self, config):
        dmobj = config['model'].ensure_object(self.path)

        for o in dmobj.parent_chain(include_self=False):
            if self.name in o.scope.vars:
                override_decl = o.scope.vars[self.name]
                return override_decl.initialization_mode(config)

        if "const" in self.flags:
            return "const"

        if str(self.path) == "/":
            return "dynamic"
        elif "static" in self.flags:
            return "dynamic"
        else:
            return "const"

    def has_prev_decl(self, decl):
        if self.prev_decl is None:
            return False
        elif decl == self.prev_decl:
            return True
        else:
            return self.prev_decl.has_prev_decl( decl )

    def usage(self, config):
        return Identifier(self)

class DMObject(object):
    def __init__(self, path):
        self.path = path

        self.obj_trunk = None
        self.obj_leaves = []

        self.procs = []
        self.vars = []

        self.scope = Scope()
        self.scope.owner = self

    def iter_leaves(self):
        for leaf in self.obj_leaves:
            yield leaf
            yield from leaf.iter_leaves()

    def parent_chain(self, include_self=True):
        if include_self:
            cnode = self
        else:
            cnode = self.obj_trunk
        while cnode is not None:
            yield cnode
            cnode = cnode.obj_trunk

    def topmost_var_decl(self, name):
        for node in reversed(list(self.parent_chain())):
            if name in node.scope.vars:
                return node
        return None

    def new_parent(self, obj_trunk):
        self.obj_trunk = obj_trunk
        obj_trunk.obj_leaves.append( self )
        self.scope.trunk = obj_trunk.scope

    def remove_child(self, obj_leaf):
        if obj_leaf in self.obj_leaves:
            self.obj_leaves.remove(obj_leaf)

    def add_proc(self, decl):
        self.procs.append(decl)
        self.scope.def_proc(decl.name, decl)

    def add_var(self, decl):
        self.vars.append(decl)
        self.scope.def_var(decl.name, decl)

    def would_override_var(self, name):
        for dmobj in self.parent_chain():
            if name in dmobj.scope.vars:
                return dmobj.scope.vars[name]
        return False

    def would_override_proc(self, name):
        for dmobj in self.parent_chain():
            if name in dmobj.scope.procs:
                return dmobj.scope.procs[name]
        return False

    def compute_overrides(self, known_vars={}, known_procs={}):
        known_vars = known_vars.copy()
        known_procs = known_procs.copy()

        for decl in self.vars:
            if decl.name in known_vars:
                decl.is_override = True
            else:
                decl.is_override = False
            known_vars[decl.name] = decl

        for decl in self.procs:
            if decl.name in known_procs:
                decl.is_override = True
            else:
                decl.is_override = False
            known_procs[decl.name] = decl

        for leaf_obj in self.obj_leaves:
            leaf_obj.compute_overrides(known_vars=known_vars, known_procs=known_procs)


class DMObjectTree(DMObject):
    def __init__(self):
        super().__init__(Path([]))
        self.objects_by_path = {}

    def iter_leaves(self):
        yield from []

    def ensure_object(self, path):
        trunk_obj = None
        for ppath in path.parent_paths():
            if ppath not in self.objects_by_path:
                o = DMObject(ppath)
                if path.is_toplevel_tree():
                    o.scope.trunk = self.scope
                o.obj_trunk = trunk_obj
                if o not in self.obj_leaves:
                    self.obj_leaves.append( o )
                self.objects_by_path[ppath] = o
            trunk_obj = self.objects_by_path[ppath]
        return self.get_object(path)

    def compute_overrides(self):
        known_vars = {}
        known_procs = {}
        for decl in self.vars:
            decl.is_override = False
        for decl in self.procs:
            if decl.name in known_procs:
                decl.is_override = True
            else:
                decl.is_override = False 
            known_procs[decl.name] = decl

        for path, dmobj in self.objects_by_path.items():
            if dmobj.obj_trunk is None:
                dmobj.compute_overrides()

    def get_object(self, path):
        if path.is_root():
            return self
        if path not in self.objects_by_path:
            raise Exception(str(path))
        return self.objects_by_path[path]
