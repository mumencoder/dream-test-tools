
from .Errors import *

class Usage:
    class Expr:
        class Identifier:
            def get_usage( self, scope ):
                try:
                    usage = [scope.resolve_usage( self )]
                except UsageError as e:
                    self.errors.append( e )
                    return []
                return usage
        class GlobalIdentifier:
            def get_usage( self, scope ):
                try:
                    usage = [scope.resolve_usage( self )]
                except UsageError as e:
                    self.errors.append( e )
                    return []
                return usage

    def no_usage(self, scope):
        return []

    def op_usage(self, scope):
        usages = []
        for expr in self.exprs:
            usages = expr.get_usage(scope)
        return usages