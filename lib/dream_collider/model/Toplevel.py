
import collections, random

from . import *

class ValidationRandomizer(object):
    def __init__(self, pass_chance=None):
        self.should_compile = True
        self.modified_validations = []
        self.pass_chance = pass_chance

    def try_modify_validation(self, vname):
        if random.random() < self.pass_chance:
            self.should_compile = False
            self.modified_validations.append(vname)
            return True
        return False

class Toplevel(object):
    def __init__(self):
        self.obj_tree = DMObjectTree()
        self.op_info = OpInfo()

        self.decls = []
        self.usr_decls = []
        self.decls_index = collections.defaultdict(list)
        self.values = {}

        self.decl_deps = collections.defaultdict(set)

        self.new_decl_vrandomizer = ValidationRandomizer(pass_chance=0.1)
        self.use_decl_vrandomizer = ValidationRandomizer(pass_chance=0.001)

    def __str__(self):
        display = ""
        for decl in self.decls:
            s = str(decl)
            if s != "":
                display += str(decl) + "\n"
        return display

    def should_compile(self):
        if self.new_decl_vrandomizer.should_compile is False:
            return False
        if self.use_decl_vrandomizer.should_compile is False:
            return False
        return True

    def modified_validations(self):
        return self.new_decl_vrandomizer.modified_validations + self.use_decl_vrandomizer.modified_validations

    def get_op(self, name):
        return self.op_info.ops[name]

    def ensure_object(self, path):
        return self.obj_tree.ensure_object( path )

    def parent_type(self, trunk_path, leaf_path):
        trunk = self.ensure_object(trunk_path)
        leaf = self.ensure_object(leaf_path)
        old_trunk = leaf.obj_trunk
        if old_trunk is not None:
            old_trunk.remove_child( leaf )
        leaf.new_parent( trunk )

    # declarations
    def can_add_decl(self, new_decl):
        if type(new_decl) is ObjectVarDecl:
            dmobj = self.obj_tree.ensure_object( new_decl.path )
            if type(dmobj) is DMObjectTree:
                if new_decl.name in dmobj.scope.vars:
                    return self.new_decl_vrandomizer.try_modify_validation("cannot override a global var")

            for dmobj_leaf in dmobj.parent_chain():
                for override_decl in dmobj_leaf.vars:
                    if override_decl.name != new_decl.name:
                        continue
                    if override_decl.allow_override is False:
                        return self.new_decl_vrandomizer.try_modify_validation("decl does not allow overrides")
                    if "const" in override_decl.flags or "static" in override_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation("cannot override const/static var")
                    if override_decl.flags != new_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation("override flags must match")

            for dmobj_leaf in dmobj.iter_leaves():
                for decl in dmobj_leaf.vars:
                    if decl.name != new_decl.name:
                        continue
                    if decl.flags != new_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation("new trunk decl flags must match with any leaf decls")

        if type(new_decl) is ProcDecl:
            dmobj = self.obj_tree.ensure_object( new_decl.path )
            override_decl = dmobj.would_override_proc(new_decl.name)
            if override_decl:
                if override_decl.allow_override is False:
                    return self.new_decl_vrandomizer.try_modify_validation("decl does not allow overrides")
        return True

    def add_decl(self, decl):
        dmobj = self.obj_tree.ensure_object( decl.path )
        if len(self.decls) > 0:
            prev_decl = self.decls[-1]
            decl.prev_decl = prev_decl
        else:
            decl.prev_decl = None
        if type(decl) is ObjectVarDecl:
            dmobj.add_var( decl )
            self.decls_index[ ("var", decl.path, decl.name) ].append( decl )
        elif type(decl) is ProcDecl:
            dmobj.add_proc( decl )
            self.decls_index[ ("proc", decl.path, decl.name) ].append( decl )
        else:
            raise Exception("unknown decl type")
        self.decls.append( decl )
        if decl.stdlib is False:
            self.usr_decls.append( decl )

    def can_use_decl(self, config, scope_decl, use_decl):
        if "static" in scope_decl.flags and str(use_decl.path) != "/":
            return self.use_decl_vrandomizer.try_modify_validation("implicit src not allowed in static var initializations")

        # currently not allowing initializations with references to forward declarations
        if not scope_decl.has_prev_decl( use_decl ):
            return False

        const_initial = scope_decl.const_initialization(config)
        dmobj = self.ensure_object(scope_decl.path)
        if type(use_decl) is ObjectVarDecl:
            if scope_decl.name == use_decl.name:
                return self.use_decl_vrandomizer.try_modify_validation("no self-reference in initialization")

            if "static" in scope_decl.flags and use_decl.flags == []:
                return self.use_decl_vrandomizer.try_modify_validation("static vars do not have global access")

            use_decl_scope = dmobj.scope.find_var(use_decl.name)
            if use_decl_scope is None:
                return self.use_decl_vrandomizer.try_modify_validation("variable not in scope")
            if use_decl_scope.vars[use_decl.name] != use_decl:
                return self.use_decl_vrandomizer.try_modify_validation("variable is shadowed")
            if dmobj.scope.get_value(use_decl.name) is None:
                return self.use_decl_vrandomizer.try_modify_validation("variable has not been initialized")

            const_usage = use_decl.const_usage()
            if not const_usage and const_initial:
                return self.use_decl_vrandomizer.try_modify_validation("a non-const usage in a const initialization")
            if self.dep_cycle_check( scope_decl, use_decl ) is True:
                return self.use_decl_vrandomizer.try_modify_validation("this would create an initialization dependency cycle")
        elif type(use_decl) is ProcDecl:
            if const_initial:
                return self.use_decl_vrandomizer.try_modify_validation("proc calls not allowed in const expressions")
            use_decl_scope = dmobj.scope.find_proc(use_decl.name)
            if use_decl_scope is None:
                return self.use_decl_vrandomizer.try_modify_validation("proc not in scope")
            if use_decl_scope.procs[use_decl.name] != use_decl:
                return self.use_decl_vrandomizer.try_modify_validation("proc is shadowed")
        else:
            raise Exception("unknown use_decl type")

        return True

    # overrides
    def compute_overrides(self):
        self.obj_tree.compute_overrides()

    # dependency analysis
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
