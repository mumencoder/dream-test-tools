
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