
import collections, random

from . import *

class ValidationRandomizer(object):
    def __init__(self, pass_chance=None):
        self.pass_chance = pass_chance

    def try_modify_validation(self, result, vname):
        if random.random() < self.pass_chance:
            result.update( { "should_compile":False, "valid":True, "notes":[vname] } )
            return result

        result.update( { "should_compile":False, "valid":False, "notes":[vname] } )
        return result

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
        self.initial_vrandomizer = ValidationRandomizer(pass_chance=0.01 * config['test.error_factor'])
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

        if orig_decl.stdlib or new_decl.stdlib:
            return True
        if "const" in orig_set:
            return False
        if "static" in orig_set:
            return False

        return True

    # declarations
    def can_add_decl(self, config, new_decl):
        result = {'notes':[]}
        loc = f"{new_decl.path}/{new_decl.name}"
        if type(new_decl) is ObjectVarDecl:
            dmobj = self.obj_tree.ensure_object( new_decl.path )

            if new_decl.name in dmobj.scope.vars:
                if type(dmobj) is DMObjectTree:
                    return self.new_decl_vrandomizer.try_modify_validation(result, f"cannot override a global var - {loc}")

               
            for dmobj_trunk in dmobj.parent_chain():
                for override_decl in dmobj_trunk.vars:
                    if override_decl.name != new_decl.name:
                        continue
                    if override_decl.allow_override is False:
                        return self.new_decl_vrandomizer.try_modify_validation(result, f"decl does not allow compile time initialization - {loc}")

            for dmobj_leaf in dmobj.iter_leaves():
                for leaf_decl in dmobj_leaf.vars:
                    if leaf_decl.name != new_decl.name:
                        continue
                    if leaf_decl.flags != new_decl.flags:
                        if not self.valid_override_flag_pairs( new_decl, leaf_decl ):
                            return self.new_decl_vrandomizer.try_modify_validation(result, f"new trunk decl flags must match with any leaf decls - {loc}")

        if type(new_decl) is ProcDecl:
            dmobj = self.obj_tree.ensure_object( new_decl.path )
            override_decl = dmobj.would_override_proc(new_decl.name)
            if override_decl:
                if override_decl.allow_override is False:
                    return self.new_decl_vrandomizer.try_modify_validation(result, f"decl does not allow overrides - {loc}")

        result.update( { "should_compile":True, "valid":True, "notes":[] } )
        return result

    def validate_decl(self, config, decl):
        result = {'notes':[]}
        loc = f"{decl.path}/{decl.name}"
        dmobj = self.obj_tree.ensure_object( decl.path )
        if type(decl) is ObjectVarDecl:
            topmost_decl = dmobj.topmost_var_decl(decl.name)

            if type(dmobj) is not DMObjectTree and topmost_decl is not None:
                topmost_dmobj = self.obj_tree.ensure_object( topmost_decl.path )
                if dmobj in topmost_dmobj.parent_chain(): 
                    topmost_decl = decl
                    topmost_dmobj = self.obj_tree.ensure_object( decl.path )

                topmost_def_decl = topmost_dmobj.scope.first_vars[decl.name]

                if topmost_def_decl != decl and decl.stdlib is False:
                    if "static" in topmost_def_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation(result, f"redefinition of global var - static {loc}")
                    if "const" in topmost_def_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation(result, f"redefinition of global var - const {loc}")

                    for dmobj_leaf in dmobj.iter_leaves():
                        for leaf_decl in dmobj_leaf.vars:
                            if leaf_decl.name != decl.name:
                                continue
                            if "const" in topmost_def_decl.flags or "static" in topmost_def_decl.flags:
                                return self.new_decl_vrandomizer.try_modify_validation(result, f"cannot override const/static var - {loc}")
                            if topmost_def_decl.flags != leaf_decl.flags:
                                if not self.valid_override_flag_pairs( topmost_def_decl, leaf_decl ):
                                    return self.new_decl_vrandomizer.try_modify_validation(result, f"override flags must match - {loc}")
                    if "const" in topmost_def_decl.flags or "static" in topmost_def_decl.flags:
                        return self.new_decl_vrandomizer.try_modify_validation(result, f"cannot override const/static var - {loc}")
                    if topmost_def_decl.flags != decl.flags:
                        if not self.valid_override_flag_pairs( topmost_def_decl, decl ):
                            return self.new_decl_vrandomizer.try_modify_validation(result, f"override flags must match - {loc}")

        elif type(decl) is ProcDecl:
            # NOTE: this is not understood, byond bug maybe?
            if type(dmobj) is DMObjectTree:
                datum_dmobj = self.obj_tree.ensure_object( Path(["datum"]) )
                if decl.name in datum_dmobj.scope.procs and dmobj.scope.first_procs[decl.name] != decl:
                    return self.new_decl_vrandomizer.try_modify_validation(result, f"bad proc override - {loc}")

        result.update( { "should_compile":True, "valid":True, "notes":[] } )
        return result

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

    def can_use_decl(self, config, def_decl, use_decl):
        result = {"decl":use_decl}
        loc = f"scope: {def_decl.path}/{def_decl.name} , use: {use_decl.path}/{use_decl.name}"
        # currently not allowing initializations with references to forward declarations
        if not def_decl.has_prev_decl( use_decl ):
            result.update( { "should_compile":None, "valid":False, "notes":None } )
            return result

        def_dmobj = self.ensure_object(def_decl.path)
        use_dmobj = self.ensure_object(use_decl.path)
        if type(use_decl) is ObjectVarDecl:
            use_decl_scope = def_dmobj.scope.find_var(use_decl.name)

            if use_decl_scope is None:
                return self.use_decl_vrandomizer.try_modify_validation(result, f"variable not in scope - {loc}")
            # variable is shadowed 
            if use_decl_scope.vars[use_decl.name] != use_decl:
                return self.can_use_decl(config, def_decl, use_decl_scope.vars[use_decl.name])

            if type(def_dmobj) is DMObjectTree:
                topmost_def = def_dmobj
            else:
                topmost_def = def_dmobj.topmost_var_decl(def_decl.name)
            topmost_def_decl = topmost_def.scope.first_vars[def_decl.name]

            if type(use_dmobj) is DMObjectTree:
                topmost_use = use_dmobj
            else:
                topmost_use = use_dmobj.topmost_var_decl(use_decl.name)
            topmost_use_decl = topmost_use.scope.first_vars[use_decl.name]

            if topmost_def_decl.initialization_mode(config) == "const":
                if "const" not in topmost_use_decl.flags:
                    return self.use_decl_vrandomizer.try_modify_validation(result, f"non-const usage in const init (no const flag) - {loc}")
                if use_decl.value is None:
                    return self.use_decl_vrandomizer.try_modify_validation(result, f"variable has not been initialized - {loc}")

            if topmost_def_decl.initialization_mode(config) == "dynamic":
                if "static" in topmost_def_decl.flags:
                    if type(topmost_use) is not DMObjectTree:
                        if topmost_use_decl.stdlib:
                            pass
                        elif "const" not in topmost_use_decl.flags and "static" not in topmost_use_decl.flags:
                            return self.use_decl_vrandomizer.try_modify_validation(result, f"non-global usage in dynamic init - {loc}")
                else:
                    if type(topmost_use) is DMObjectTree:
                        pass
                    elif "const" in topmost_use_decl.flags:
                        pass
                    else:
                        return self.use_decl_vrandomizer.try_modify_validation(result, f"non-const usage in dynamic init - {loc}")

            if def_decl.name == use_decl.name:
                return self.use_decl_vrandomizer.try_modify_validation(result, f"no self-reference in initialization - {loc}")

            if self.dep_cycle_check( def_decl, use_decl ) is True:
                return self.use_decl_vrandomizer.try_modify_validation(result, f"this would create an initialization dependency cycle - {loc}")
        elif type(use_decl) is ProcDecl:
            use_decl_scope = def_dmobj.scope.find_proc(use_decl.name)
            if use_decl_scope is None:
                return self.use_decl_vrandomizer.try_modify_validation(result, f"proc not in scope - {loc}")
            # proc is shadowed
            if use_decl_scope.procs[use_decl.name] != use_decl:
                return self.can_use_decl(config, def_decl, use_decl_scope.procs[use_decl.name])

            if def_decl.initialization_mode(config) == "const":
                return self.use_decl_vrandomizer.try_modify_validation(result, f"a non-const usage in a const initialization - {loc}")
            if str(def_decl.path) != "/" and str(use_decl.path) != "/":
                return self.use_decl_vrandomizer.try_modify_validation(result, f"implicit src for proc call - {loc}")
        else:
            raise Exception("unknown use_decl type")

        result.update( { "should_compile":True, "valid":True, "notes":[] } )
        return result

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
