
import collections

from . import *

class Toplevel(object):
    def __init__(self):
        self.obj_tree = DMObjectTree()
        self.op_info = OpInfo()

        self.decls = []

        self.values = {}

        self.decl_deps = collections.defaultdict(set)

    def __str__(self):
        display = ""
        for decl in self.decls:
            s = str(decl)
            if s != "":
                display += str(decl) + "\n"
        return display

    def get_op(self, name):
        return self.op_info.ops[name]

    def in_scope(self, scope_path, var_path):
        return scope_path.contains(var_path) 

    def dep_cycle_check(self, v1, v2):
        if v1 == v2: 
            return True

        checking_vars = set([v2])
        checked_vars = set()

        while len(checking_vars) > 0:
            for v in checking_vars:
                if v not in checked_vars:
                    next_var = v
                    break
            if v1 in self.decl_deps:
                return True
            for v in self.decl_deps[next_var]:
                if v in checked_vars:
                    continue
                checking_vars.add(v)
            checked_vars.add(next_var)
            checking_vars.remove(next_var)
        return False

    def add_dep(self, v1, v2):
        self.decl_deps[v1].add( v2 )

    def dep_id(self, decl):
        return f"{typeof(decl)}-{decl.path}-{decl.name}"

    def decl_usage(self, decl):
        if type(decl) is ProcDecl:
            return CallExpression(decl.name)
        else:
            return Identifier(decl.name)

    def ensure_object(self, path):
        return self.obj_tree.ensure_object( path )

    def parent_type(self, trunk_path, leaf_path):
        trunk = self.ensure_object(trunk_path)
        leaf = self.ensure_object(leaf_path)
        old_trunk = leaf.obj_trunk
        old_trunk.remove_child( leaf )
        leaf.new_parent( trunk )

    def add_decl(self, decl):
        dmobj = self.obj_tree.ensure_object( decl.path )
        if len(self.decls) > 0:
            prev_decl = self.decls[-1]
            decl.prev_decl = prev_decl
            dmobj.add_var( decl.name )
        else:
            decl.prev_decl = None
        self.decls.append( decl )

    def ident_in_scope(self, ident):
        dmobj = self.obj_tree.get_object( self.scope )
        while dmobj is not None:
            if dmobj.has_var(ident):
                return True
            dmobj = dmobj.obj_trunk
        return False

    def set_value(self, decl, value):
        self.values[ (str(decl.path), str(decl.name)) ] = value

    def get_value(self, ident):
        dmobj = self.obj_tree.get_object( self.scope )
        while dmobj is not None:
            v = self.values.get( (str(dmobj.path), ident) )
            if v is not None:
                return v
            dmobj = dmobj.obj_trunk
        return None

