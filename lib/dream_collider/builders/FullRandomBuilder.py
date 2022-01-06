
import random, time

import Shared

from ..model import *
from . import *  

class FullRandomBuilder(object):
    def __init__(self):
        self.otree_builder = ObjectTreeBuilder()
        for path in ['/', '/datum', '/atom', '/area', '/obj']:
            self.otree_builder.add_path(path)
      
        self.const_builder = ConstExprBuilder()
        self.ops = ["+", "-", "*", "/"]

        self.expr_ty = Shared.Random.to_choices( {"var":0.5, "int":0.5 } )
        
    def leaf_expr(self, config, tries=20):
        expr_ty = Shared.Random.choose_choices(self.expr_ty, 1)[0]
        if expr_ty == "var":
            while tries > 0:
                decl = random.choice( config['model'].usr_decls )
                tries -= 1

                # TODO: should be able to call stdlib stuff
                if decl.stdlib:
                    continue

                if not config['model'].can_use_decl(config, config['scope_decl'], decl):
                    continue

                expr = decl.usage(config)
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
        config['model'] = Toplevel()
        self.stdlib_builder = StdlibBuilder(config['model'])

        for path in self.otree_builder.possible_paths:
            config['model'].ensure_object(path)
        self.otree_builder.defaults(config)

#        print("=======1")
        for i in range(0,n_stmts):
            decl = self.otree_builder.decl(config) 
            config['model'].add_decl( decl )
#            print( "process decl", decl.name, decl.path, type(decl))


#        for o in config['model'].obj_tree.iter_leaves():
#            print(o.path, [d.name for d in o.scope.get_usr_vars()])

#        print("=======2")
        for decl in config['model'].usr_decls:
            config['scope_decl'] = decl
            if type(decl) is ObjectVarDecl:
                dmobj = config['model'].ensure_object(decl.path)
                config['scope'] = dmobj.scope
#                print( "process decl", decl.name, decl.path, decl.flags)
                while True:
                    decl.initial = self.expr(config, depth=4)
#                    print(decl.initial)
                    if decl.const_initialization(config) or decl.initial.is_const(config):
                        try:
                            result = decl.initial.eval(config)
#                            print("set", dmobj.path, decl.name)
                            dmobj.scope.set_value( decl.name, result )
                        except GenerationError:
                            continue
                    break
                del config['scope']

        config['model'].compute_overrides()
        
        result = str(config['model'])
        result += """
/proc/main()
    return
"""
        return result