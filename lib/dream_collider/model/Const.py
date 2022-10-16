
from ..common import *

from .ast import *

class Const(object):
    def always_const(self, scope):
        return True

    def never_const(self, scope):
        return False
    
    def subtree_const(self, scope):
        for node in AST.iter_subtree(self):
            if not node.is_const(scope):
                return False
        return True

    class Identifier(object):
        def is_const(self, scope):
            if scope.get_usage(self).initialization_mode() == "const":
                return True
            else:
                return False
                
for ty in iter_types(AST.Expr):
    ty.is_const = Const.never_const

for ty in iter_types(AST.Op):
    ty.is_const = Const.subtree_const
    
for ty in [AST.Expr.Integer, AST.Expr.Float]:
    ty.is_const = Const.always_const

for ty_name in ["LessThan", "LessEqualThan", "GreaterThan", "GreaterEqualThan", 
    "Equals", "NotEquals", "NotEquals2", "Equivalent", "NotEquivalent"]:
    ty = getattr(AST.Op, ty_name)
    ty.is_const = Const.never_const

AST.Op.To.is_const = Const.never_const
AST.Op.In.is_const = Const.never_const