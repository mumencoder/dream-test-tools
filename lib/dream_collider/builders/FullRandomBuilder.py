
import random, time

import Shared

from ..model import *
from . import *  

class FullRandomBuilder(object):
    def __init__(self):
        self.otree_builder = ObjectTreeBuilder()
        for path in ['/', '/datum', '/atom', '/area', '/turf', '/obj', '/mob']:
            self.otree_builder.add_path(path)
      
        self.const_builder = ConstExprBuilder()
        self.ops = ["+", "-", "*", "/"]

        self.expr_ty = Shared.Random.to_choices( {"var":0.5, "int":0.5 } )
        
    def leaf_expr(self, config, tries=20):
        expr_ty = Shared.Random.choose_choices(self.expr_ty, 1)[0]
        if expr_ty == "var":
            while tries > 0:
                tries -= 1
                decl = random.choice( config['model'].decls )

                # TODO: should be able to call stdlib stuff
                if decl.stdlib:
                    continue
                const_initial = config['decl'].const_initialization()

                # BAD: model wont allow it
                if config['model'].can_use_decl(decl):
                    continue

                if type(decl) is ObjectVarDecl:
                    const_usage = decl.const_usage()
                    # BAD: a non-const usage in a const initialization
                    if not const_usage and const_initial:
                        continue
                    # BAD: this would create an initialization dependency cycle
                    if config['model'].dep_cycle_check( config['decl'], decl ) is True:
                        continue

                # BAD: currently not allowing initializations with references to forward declarations
                if decl.has_prev_decl( config['decl'] ):
                    continue
                # BAD: decl is not in scope
                if not config['model'].in_scope( config['decl'].path, decl.path):
                    continue

                expr = config['model'].decl_usage( decl )
                # BAD: proc calls not allowed in const expressions
                if type(expr) is CallExpression and const_initial:
                    continue
                # BAD: implicit source not allowed
                if "static" in config['decl'].flags and str(decl.path) != "/":
                    continue
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
        start_time = time.time()

        config['model'] = Toplevel()
        self.stdlib_builder = StdlibBuilder(config['model'])

        for path in self.otree_builder.possible_paths:
            config['model'].ensure_object(path)
        self.otree_builder.defaults(config)

        for i in range(0,n_stmts):
            config['model'].add_decl( self.otree_builder.decl(config) )

        config['model'].compute_overrides()

        for decl in config['model'].decls:
            config['decl'] = decl
            if type(decl) is ObjectVarDecl:
                while True:
                    decl.initial = self.expr(config, depth=4)
                    if decl.const_initialization() or decl.initial.is_const(config):
                        config['model'].scope = decl.path
                        try:
                            result = decl.initial.eval(config)
                            config['model'].set_value( decl, result )
                        except GenerationError:
                            continue
                    break

        del config['decl']
        result = str(config['model'])
        result += """
/proc/main()
    return
"""
        #print(f"testgen in {time.time() - start_time}")
        return result