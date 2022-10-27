
from ..common import *

from .ast import *

class ODValidate(object):
    class Op(object):
        class In(object):
            def od_validate(self, scope):
                if type(self.exprs[1]) in [AST.Expr.String, AST.Expr.Integer, AST.Expr.Float]:
                    return False
                return ODValidate.od_validate_subtree(self, scope)

    def od_validate_subtree(self, scope):
        for snode in AST.iter_subtree(self):
            if snode.validate( scope ) is False:
                return False
        return True