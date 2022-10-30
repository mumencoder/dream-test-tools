
from ..common import *

from .ast import *

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

class ODValidate(object):
    def od_validate_subtree(self):
        for snode in AST.iter_subtree(self):
            if snode.od_validate( ) is False:
                return False
        return True

    class Op(object):
        class In(object):
            def od_validate(self):
                if type(self.exprs[1]) in [AST.Expr.String, AST.Expr.Integer, AST.Expr.Float, AST.Expr.Null]:
                    return False
                return ODValidate.od_validate_subtree(self)

        class To(object):
            def od_validate(self):
                return False

        class Power(object):
            def od_validate(self):
                return False

        class Divide(object):
            def od_validate(self):
                if type(self.exprs[1]) is AST.Expr.Integer:
                    if self.exprs[1].n == 0:
                        return False
                if type(self.exprs[1]) is AST.Expr.Float:
                    if self.exprs[1].n == 0.0:
                        return False
                return True

        class Modulus(object):
            def od_validate(self):
                if type(self.exprs[1]) is AST.Expr.Integer:
                    if self.exprs[1].n == 0:
                        return False
                if type(self.exprs[1]) is AST.Expr.Float:
                    if int(self.exprs[1].n) == 0:
                        return False
                return True