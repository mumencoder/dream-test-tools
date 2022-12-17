
class SemanticError(Exception):
    pass

class GeneralError(SemanticError):
    def __init__(self, error_code):
        self.error_code = error_code
        
class ConstError(SemanticError):
    def __init__(self, scope, expr, error_code):
        self.scope = scope
        self.expr = expr
        self.error_code = error_code

class UsageError(SemanticError):
    def __init__(self, scope, node, error_code):
        self.scope = scope
        self.node = node
        self.error_code = error_code