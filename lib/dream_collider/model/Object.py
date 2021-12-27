
import random 

from ..common import *
from ..model import *

class ObjectVarDecl(object):
    def __init__(self):
        self.path = None
        self.name = None
        self.flags = []
        self.initial = None

        self.stdlib = False

    def __str__(self):
        if self.stdlib is True:
            return ""
            
        if len(self.path.segments) != 0:
            path = str(self.path) + '/'
        else:
            path = ""
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

    def const_initialization(self):
        return "const" in self.flags or self.flags in [[], ["tmp"]]

    def const_usage(self):
        return self.flags not in [[], ["tmp"], ["static"], ["static","tmp"]]

    def has_prev_decl(self, decl):
        if decl == self: 
            return True
        elif self.prev_decl is None:
            return False
        else:
            return self.prev_decl.has_prev_decl( decl )

   
class DMObject(object):
    def __init__(self, path):
        self.path = path

        self.obj_trunk = None
        self.obj_leaves = []

        self.vars = {}
        self.procs = {}

    def parent_chain(self):
        cnode = self
        while cnode is not None:
            yield cnode
            cnode = cnode.obj_trunk

    def new_parent(self, obj_trunk):
        self.obj_trunk = obj_trunk

    def remove_child(self, obj_leaf):
        if obj_leaf in self.obj_leaves:
            self.obj_leaves.remove(obj_leaf)

    def add_var(self, name):
        self.vars[name] = True

    def has_var(self, name):
        return name in self.vars

class DMObjectTree(DMObject):
    def __init__(self):
        super().__init__(Path([]))
        self.objects_by_path = {self.path:self}

    def ensure_object(self, path):
        trunk_obj = self
        for ppath in path.parent_paths():
            if ppath not in self.objects_by_path:
                o = DMObject(ppath)
                o.obj_trunk = trunk_obj
                self.objects_by_path[ppath] = o
            trunk_obj = self.objects_by_path[ppath]
        return self.get_object(path)

    def get_object(self, path):
        if path not in self.objects_by_path:
            raise Exception(str(path))
        return self.objects_by_path[path]
