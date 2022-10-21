
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