
from ..common import *

from .ast import *

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
            AST.print( self, s, seen=set() )
            print(s.getvalue())
            return self.eval(scope)