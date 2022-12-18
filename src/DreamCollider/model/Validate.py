
from .Errors import *
from .dmast import *

class Validate:
    class Expr:
        class Path:
            def validate(self):
                self.errors.append( GeneralError('UNDEF_TYPEPATH')  )

    class Op:
        class In:
            def validate(self):
                Validate.subtree_valid(self)
                self.errors.append( GeneralError('UNEXPECTED_IN') )

    def subtree_valid(self):
        for node in AST.walk_subtree(self):
            if node is self:
                continue
            node.validate()