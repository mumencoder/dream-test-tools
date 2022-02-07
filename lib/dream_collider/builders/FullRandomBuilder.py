
import random, time

import Shared

from ..model import *
from . import *  

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