
from ..common import *

from .ast import *

num_type = [AST.Expr.Float, AST.Expr.Integer]

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

        class Equivalent(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.String]):
                    return False
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                if sym_check_bin_op(self, [AST.Expr.String], num_type):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.Null]):
                    return False
                if sym_check_bin_op(self, [AST.Expr.Null], num_type):
                    return False
                if check_bin_op(self, num_type, num_type):
                    return False
                return ODValidate.od_validate_subtree(self)

        class NotEquivalent(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.String]):
                    return False
                if check_bin_op(self, num_type, num_type):
                    return False
                if sym_check_bin_op(self, num_type, [AST.Expr.String]):
                    return False
                if sym_check_bin_op(self, [AST.Expr.Null], num_type):
                    return False
                if sym_check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class Negate(object):
            def od_validate(self):
                if type(self.exprs[0]) in [AST.Expr.String, AST.Expr.Null]:
                    return False
                return ODValidate.od_validate_subtree(self)

        class BitAnd(object):
            def od_validate(self):
                if check_bin_op(self, num_type, num_type):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.Null]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class BitXor(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, num_type, num_type):
                    return False
                if sym_check_bin_op(self, [AST.Expr.Null], num_type):
                    return False
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class BitOr(object):
            def od_validate(self):
                if check_bin_op(self, num_type, num_type):
                    return False
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                if sym_check_bin_op(self, [AST.Expr.Null], num_type):
                    return False
                return ODValidate.od_validate_subtree(self)

        class BitNot(object):
            def od_validate(self):
                if type(self.exprs[0]) in num_type:
                    return False
                return ODValidate.od_validate_subtree(self)

        class Not(object):
            def od_validate(self):
                if type(self.exprs[0]) in num_type:
                    return False
                return ODValidate.od_validate_subtree(self)

        class Subtract(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.Null]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class Multiply(object):
            def od_validate(self):
                if check_bin_op(self, num_type, [AST.Expr.String]):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.Null]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class Divide(object):
            def od_validate(self):
                if type(self.exprs[1]) in [AST.Expr.Null]:
                    return False
                if type(self.exprs[1]) in [AST.Expr.String]:
                    return False
                return ODValidate.od_validate_subtree(self)

        class Modulus(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], num_type):
                    return False
                return ODValidate.od_validate_subtree(self)

        # TODO: value ranges
        class Power(object):
            def od_validate(self):
                if check_bin_op(self, num_type, [AST.Expr.String]):
                    return False
                if type(self.exprs[0]) in [AST.Expr.Null] or type(self.exprs[1]) in [AST.Expr.Null]:
                    return False
                return ODValidate.od_validate_subtree(self)

        class LessThan(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class LessEqualThan(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class GreaterThan(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class GreaterEqualThan(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.Null], [AST.Expr.String]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class ShiftLeft(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.String]):
                    return False
                if check_bin_op(self, num_type, num_type):
                    return False
                if sym_check_bin_op(self, [AST.Expr.String], num_type):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, num_type, [AST.Expr.Null]):
                    return False
                return ODValidate.od_validate_subtree(self)

        class ShiftRight(object):
            def od_validate(self):
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.String]):
                    return False
                if check_bin_op(self, num_type, num_type):
                    return False
                if sym_check_bin_op(self, [AST.Expr.String], num_type):
                    return False
                if check_bin_op(self, [AST.Expr.String], [AST.Expr.Null]):
                    return False
                if check_bin_op(self, num_type, [AST.Expr.Null]):
                    return False
                return ODValidate.od_validate_subtree(self)

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