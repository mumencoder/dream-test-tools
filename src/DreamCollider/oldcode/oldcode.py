class Expr:
    def choose_scoped_identifier(self, env, expr):
        scope = env.attr.gen.scope
        if type(scope) is AST.Toplevel:
            var_defines = list(scope.get_vars())
            if len(var_defines) == 0:
                raise GenerationError()
            var_decl = random.choice( random.choice( var_defines ) )
            return var_decl.name
        elif type(expr) is AST.Expr.GlobalIdentifier:
            var_defines = list(scope.root.get_vars())
            if len(var_defines) == 0:
                raise GenerationError()
            var_decl = random.choice( random.choice( var_defines ) )
            return var_decl.name
        elif type(scope) is AST.ObjectBlock:
            blocks = scope.root.object_blocks_by_path[scope.path]
            if len(blocks) == 0:
                raise GenerationError()
            block = random.choice( blocks )
            block = random.choice( list(block.parent_chain()) )
            var_defines = list(scope.get_vars()) 
            if len(var_defines) == 0:
                raise GenerationError()
            var_decl = random.choice( random.choice( var_defines ) )
            return var_decl.name
        else:
            raise Exception("bad scope")
            
class ObjectVarDecl(object):
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

class ValidationRandomizer(object):
    def __init__(self, pass_chance=None):
        self.pass_chance = pass_chance

    def try_modify_validation(self, result, vname):
        if random.random() < self.pass_chance:
            result.update( { "should_compile":False, "valid":True, "notes":[vname] } )
            return result

        result.update( { "should_compile":False, "valid":False, "notes":[vname] } )
        return result

    new_decl_vrandomizer = ValidationRandomizer(pass_chance=0.1 * config['test.error_factor'])
    initial_vrandomizer = ValidationRandomizer(pass_chance=0.01 * config['test.error_factor'])
    use_decl_vrandomizer = ValidationRandomizer(pass_chance=0.001 * config['test.error_factor'])

class TopLevel(object):
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


class ObjectTreeBuilder(object):
    def __init__(self):
        self.possible_paths = []
        self.def_len = 1

        self.should_compile = True
        self.notes = []

    def add_path(self, path):
        if type(path) is str:
            self.possible_paths.append( Path.from_string(path) )
        elif type(path) is Path:
            self.possible_paths.append( path )

    def defaults(self, config):
        config['otree_builder.statement.type'] = Shared.Random.to_choices( {"var":0.8, "proc":0.2} )
        config['otree_builder.flags.static'] = 0.05
        config['otree_builder.flags.const'] = 0.05
        config['otree_builder.flags.tmp'] = 0.05

    def var_name(self, config):
        name = None
        while name in [None, "as", "if", "in", "UP", "do", "to"]:
            name = Shared.Random.generate_string(self.def_len)
        return name

    def proc_name(self, config):
        name = None
        while name in [None, "as", "if", "in", "UP", "do", "to"]:
            name = Shared.Random.generate_string(self.def_len)
        return name

    def path(self, config):
        return random.choice(self.possible_paths)

    def flags(self, config):
        flags = []

        a = random.random()
        if a < config['otree_builder.flags.static']:
            flags.append("static")
        a = random.random()
        if a < config['otree_builder.flags.const']:
            flags.append("const")
        a = random.random()
        if a < config['otree_builder.flags.tmp']:
            flags.append("tmp")
        return flags

    def decl(self, config):
        while True:
            ty = Shared.Random.choose_choices( config['otree_builder.statement.type'], 1 )[0]

            if ty == "var":
                decl = ObjectVarDecl()
                decl.path = self.path(config)
                decl.flags = self.flags(config)
                decl.name = self.var_name(config)
                result = config['model'].can_add_decl(config, decl)
                if result["valid"] is False:
                    continue
                else:
                    self.should_compile = self.should_compile and result["should_compile"]
                    self.notes += result["notes"]
                return decl
            elif ty == "proc":
                decl = ProcDecl()
                decl.path = self.path(config)
                decl.name = self.proc_name(config)
                result = config['model'].can_add_decl(config, decl)
                if result["valid"] is False:
                    continue
                else:
                    self.should_compile = self.should_compile and result["should_compile"]
                    self.notes += result["notes"]
                return decl
            else:
                raise Exception("invalid choice of statement type")


class FullRandomBuilder(object):
    def __init__(self, config):
        self.otree_builder = ObjectTreeBuilder()
        for path in ['/', '/datum', '/atom', '/area', '/obj']:
            self.otree_builder.add_path(path)
      
        self.toplevel = Toplevel(config)

        self.ops = ["+", "-", "*", "/"]

        self.expr_ty = Shared.Random.to_choices( {"var":0.5, "int":0.5 } )

        self.should_compile = True
        self.notes = []
        
    def leaf_expr(self, config, tries=20):
        expr_ty = Shared.Random.choose_choices(self.expr_ty, 1)[0]
        if expr_ty == "var":
            while tries > 0:
                decl = random.choice( config['model'].usr_decls )
                tries -= 1

                # TODO: should be able to call stdlib stuff
                if decl.stdlib:
                    continue

                result = config['model'].can_use_decl(config, config['scope_decl'], decl)
                if result["valid"] is False:
                    continue
                else:
                    self.should_compile = self.should_compile and result["should_compile"]
                    self.notes += result["notes"]

                expr = result["decl"].usage(config)
                return expr
        elif expr_ty == "int":
            return DefaultBuilder.const_int(config)
        else:
            raise Exception("unknown leaf_expr type ", expr_ty)

    def expr(self, config, depth=None, form="rval"):
        if depth == 1:
            expr = None
            while expr is None:
                expr = self.leaf_expr(config)
        else:
            expr = None
            while expr is None:
                try:
                    op = config['model'].get_op(random.choice(self.ops))
                    e = OpExpression(op)
                    for place in op.arity:
                        new_depth = random.randint(1, depth-1)
                        leaf_expr = self.expr(config, new_depth)
                        e.leaves.append( leaf_expr )
                    expr = e
                except GenerationError:
                    pass
        return expr

    def test(self, config, n_stmts):
        config['model'] = self.toplevel
        self.stdlib_builder = StdlibBuilder(config['model'])

        for path in self.otree_builder.possible_paths:
            config['model'].ensure_object(path)
        self.otree_builder.defaults(config)

        for i in range(0,n_stmts):
            decl = self.otree_builder.decl(config) 
            config['model'].add_decl( decl )

        for decl in config['model'].usr_decls:
            config['scope_decl'] = decl
            if type(decl) is ObjectVarDecl:
                dmobj = config['model'].ensure_object(decl.path)
                if type(dmobj) is DMObjectTree:
                    topmost_def = dmobj
                else:
                    topmost_def = dmobj.topmost_var_decl(decl.name)
                topmost_def_decl = topmost_def.scope.first_vars[decl.name]
                config['scope'] = dmobj.scope
                decl.initial = None
                should_compile = self.should_compile
                notes = list(self.notes)
                while decl.initial is None:
                    self.should_compile = should_compile
                    self.notes = notes
                    decl.initial = self.expr(config, depth=4)
                    try:
                        decl.initial = decl.initial.simplify(config)
                    except GenerationError:
                        self.should_compile = should_compile
                        self.notes = notes
                        retain_error = config['model'].initial_vrandomizer.try_modify_validation({}, f"generationerror - {decl.path}/{decl.name}")
                        if retain_error["valid"] is False:
                            decl.initial = None
                            continue
                        else:
                            self.should_compile = self.should_compile and retain_error["should_compile"]
                            self.notes += retain_error["notes"]
                        decl.initial = None
                        continue
                    if topmost_def_decl.initialization_mode(config) == "const" and not decl.initial.is_const(config):
                        self.should_compile = should_compile
                        self.notes = notes
                        retain_error = config['model'].initial_vrandomizer.try_modify_validation({}, f"generationerror - {decl.path}/{decl.name}")
                        if retain_error["valid"] is False:
                            decl.initial = None
                            continue
                        else:
                            self.should_compile = self.should_compile and retain_error["should_compile"]
                            self.notes += retain_error["notes"]
                    if decl.initial.is_const(config):
                        try:
                            decl.value = decl.initial.eval(config)
                        except GenerationError:
                            self.should_compile = should_compile
                            self.notes = notes
                            retain_error = config['model'].initial_vrandomizer.try_modify_validation({}, f"generationerror - {decl.path}/{decl.name}")
                            if retain_error["valid"] is False:
                                decl.initial = None
                                continue
                            else:
                                self.should_compile = self.should_compile and retain_error["should_compile"]
                                self.notes += retain_error["notes"]
                del config['scope']
            elif type(decl) is ProcDecl:
                decl.statements.append( ReturnStatement(ConstExpression(1)))
            else:
                raise Exception("Unknown declaration")
                
        for decl in config['model'].usr_decls:
            result = config['model'].validate_decl(config, decl)
            self.should_compile = self.should_compile and result["should_compile"]
            self.notes += result['notes']

        self.should_compile = self.should_compile and self.otree_builder.should_compile
        self.notes += self.otree_builder.notes

        config['model'].compute_overrides()
        
        result = str(config['model'])
        result += """
/proc/main()
    return
"""
        return result
    

            
class Evaluate(object):
    class Op(object):
        class LessThan(object):
            def eval(self, scope):
                self.eval_leaves(scope)
                if self.ev_results[0] is float and self.ev_results[1] is float:
                    return self.ev_results[0] < self.ev_results[1]
                raise RunException()
            
def check_bin_op(self, ty1, ty2):
    if type(self.exprs[0]) in ty1 and type(self.exprs[1]) in ty2:
        return True
    return False

def sym_check_bin_op(self, ty1, ty2):
    if type(self.exprs[0]) in ty1 and type(self.exprs[1]) in ty2:
        return True
    if type(self.exprs[1]) in ty1 and type(self.exprs[0]) in ty2:
        return True
    return False

class Simplify(object):
    class Op(object):
        class Divide(object):
            def after_subtree_simplify(self, scope):
                if self.exprs[1].is_const(scope) and self.exprs[1].eval(scope) in [0, -0, 0.0, -0.0]:
                    scope.add_error( self, "attempt to divide by 0" )
                    return self
                return None

        def simplify(self, scope):
            e = self.before_subtree_simplify(scope)
            if e is not None:
                return e
            for i, expr in enumerate(self.exprs):
                self.exprs[i] = expr.simplify(scope)
            e = self.after_subtree_simplify(scope)
            if e is not None:
                return e
            for expr in self.exprs:
                if not expr.is_const(scope):
                    return self
            s = io.StringIO()
            return self.eval(scope)
        
def ast_initialize():
        from .Validation import Validation
        Shared.Type.mix_fn(AST, Validation, 'validate')
        for ty in Shared.Type.iter_types(AST.Expr):
            if not hasattr(ty, 'validate'):
                ty.validate = Validation.validate_subtree
        for ty in Shared.Type.iter_types(AST.Op):
            if not hasattr(ty, 'validate'):
                ty.validate = Validation.validate_subtree

        from .ODValidate import ODValidate
        Shared.Type.mix_fn(AST, ODValidate, 'od_validate')
        for ty in Shared.Type.iter_types(AST.Expr):
            if not hasattr(ty, 'od_validate'):
                ty.od_validate = ODValidate.od_validate_subtree
        for ty in Shared.Type.iter_types(AST.Op):
            if not hasattr(ty, 'od_validate'):
                ty.od_validate = ODValidate.od_validate_subtree

        from .Simplify import Simplify  
        for ty in Shared.Type.iter_types(AST.Expr):
            ty.simplify = lambda self, scope: self
            
        for ty in Shared.Type.iter_types(AST.Op):
            if ty is AST.Op:
                continue
            ty.simplify = Simplify.Op.simplify
            if not hasattr(ty, 'before_subtree_simplify'):
                ty.before_subtree_simplify = lambda self, scope: None
            if not hasattr(ty, 'after_subtree_simplify'):
                ty.after_subtree_simplify = lambda self, scope: None    

from ..common import *
from ..model import *

class Validation(object):
    class Op(object):
        class Power(object):
            def validate(self, scope):
                e2 = self.exprs[1]
                if type(e2) is AST.Expr.Integer:
                    if abs(e2.n) > 32:
                        return False
                if type(e2) is AST.Expr.Float:
                    if abs(e2.n) > 32:
                        return False
                return Validation.validate_subtree(self, scope)

    def validate_subtree(self, scope):
        for snode in AST.iter_subtree(self):
            if snode.validate( scope ) is False:
                return False
        return True