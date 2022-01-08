
import collections, random

from . import *

class ValidationRandomizer(object):
    def __init__(self, pass_chance=None):
        self.pass_chance = pass_chance

    def try_modify_validation(self, vname):
        if random.random() < self.pass_chance:
            return { "should_compile":False, "valid":True, "notes":[vname] }
        return { "should_compile":False, "valid":False }

class Toplevel(object):
    def __init__(self, config):

        self.obj_tree = DMObjectTree()
        self.op_info = OpInfo()

        self.decls = []
        self.usr_decls = []
        self.decls_index = collections.defaultdict(list)
        self.values = {}

        self.decl_deps = collections.defaultdict(set)

        self.new_decl_vrandomizer = ValidationRandomizer(pass_chance=0.1 * config['test.error_factor'])
        self.use_decl_vrandomizer = ValidationRandomizer(pass_chance=0.001 * config['test.error_factor'])

    def __str__(self):
        display = ""
        for decl in self.decls:
            s = str(decl)
            if s != "":
                display += str(decl) + "\n"
        return display

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

    def valid_override_flag_pairs(self, orig_decl, new_decl):
        orig_set = set(orig_decl.flags)
        new_set = set(new_decl.flags)

        set_diff = list(orig_set.symmetric_difference(new_set))

        if "const" in orig_set:
            return False
        if "static" in orig_set:
            return False

        return True

    # declarations
    def can_add_decl(self, config, new_decl):
        loc = f"{new_decl.path}/{new_decl.name}"
        if type(new_decl) is ObjectVarDecl:
            dmobj = self.obj_tree.ensure_object( new_decl.path )
            if type(dmobj) is DMObjectTree:
                if new_decl.name in dmobj.scope.vars:
                    return self.new_decl_vrandomizer.try_modify_validation(f"cannot override a global var - {loc}")

            for dmobj_trunk in dmobj.parent_chain():
                for override_decl in dmobj_trunk.vars:
                    if override_decl.name != new_decl.name:
                        continue
                    if override_decl.allow_override is False:
                        return self.new_decl_vrandomizer.try_modify_validation(f"decl does not allow overrides - {loc}")
                    if "const" in override_decl.flags or "static" in override_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation(f"cannot override const/static var - {loc}")
                    if override_decl.flags != new_decl.flags:
                        if not self.valid_override_flag_pairs( override_decl, new_decl ):
                            return self.new_decl_vrandomizer.try_modify_validation(f"override flags must match - {loc}")

            for dmobj_leaf in dmobj.iter_leaves():
                for override_decl in dmobj_leaf.vars:
                    if override_decl.name != new_decl.name:
                        continue
                    if override_decl.flags != new_decl.flags:
                        if "static" not in new_decl.flags and "static" in override_decl.flags:
                            if not override_decl.initial.is_const(config):
                                return self.new_decl_vrandomizer.try_modify_validation(f"new trunk decl creates a const initialization condition - {loc}")

                        if not self.valid_override_flag_pairs( new_decl, override_decl ):
                            return self.new_decl_vrandomizer.try_modify_validation(f"new trunk decl flags must match with any leaf decls - {loc}")

        if type(new_decl) is ProcDecl:
            dmobj = self.obj_tree.ensure_object( new_decl.path )
            override_decl = dmobj.would_override_proc(new_decl.name)
            if override_decl:
                if override_decl.allow_override is False:
                    return self.new_decl_vrandomizer.try_modify_validation(f"decl does not allow overrides - {loc}")
        return { "should_compile":True, "valid":True, "notes":[] }

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
        loc = f"scope: {scope_decl.path}/{scope_decl.name} , use: {use_decl.path}/{use_decl.name}"
        # currently not allowing initializations with references to forward declarations
        if not scope_decl.has_prev_decl( use_decl ):
            return { "should_compile":None, "valid":False, "notes":None }

        dmobj = self.ensure_object(scope_decl.path)
        if type(use_decl) is ObjectVarDecl:
            use_decl_scope = dmobj.scope.find_var(use_decl.name)
            if use_decl_scope is None:
                return self.use_decl_vrandomizer.try_modify_validation(f"variable not in scope - {loc}")
            # variable is shadowed 
            if use_decl_scope.vars[use_decl.name] != use_decl:
                return self.can_use_decl(config, scope_decl, use_decl_scope.vars[use_decl.name])

            if "const" in scope_decl.flags and "const" not in use_decl.flags:
                return self.use_decl_vrandomizer.try_modify_validation(f"a non-const usage in a const initialization - {loc}")

            if "static" not in scope_decl.flags and str(scope_decl.path) != "/" and "const" not in use_decl.flags:
                return self.use_decl_vrandomizer.try_modify_validation(f"object var decls doesnt allow implicit const - {loc}")

            if "static" in scope_decl.flags and str(use_decl.path) != "/" and "const" not in use_decl.flags:
                return self.use_decl_vrandomizer.try_modify_validation(f"implicit src not allowed - {loc}")

            if scope_decl.name == use_decl.name:
                return self.use_decl_vrandomizer.try_modify_validation(f"no self-reference in initialization - {loc}")

            if dmobj.scope.get_value(use_decl.name) is None:
                return self.use_decl_vrandomizer.try_modify_validation(f"variable has not been initialized - {loc}")

            if scope_decl.initialization_mode == "const" and not use_decl.initial.is_const():
                return self.use_decl_vrandomizer.try_modify_validation(f"a non-const usage in a const initialization - {loc}")
            if self.dep_cycle_check( scope_decl, use_decl ) is True:
                return self.use_decl_vrandomizer.try_modify_validation(f"this would create an initialization dependency cycle - {loc}")
        elif type(use_decl) is ProcDecl:
            use_decl_scope = dmobj.scope.find_proc(use_decl.name)
            if use_decl_scope is None:
                return self.use_decl_vrandomizer.try_modify_validation(f"proc not in scope - {loc}")
            # proc is shadowed
            if use_decl_scope.procs[use_decl.name] != use_decl:
                return self.can_use_decl(config, scope_decl, use_decl_scope.procs[use_decl.name])

            if str(scope_decl.path) != "/" and str(use_decl.path) != "/":
                return self.use_decl_vrandomizer.try_modify_validation(f"implicit src for proc call - {loc}")
        else:
            raise Exception("unknown use_decl type")

        return { "should_compile":True, "valid":True, "notes":[] }

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
