
class Const(object):
    class ConstExpression(object):
        def is_const(self, config):
            return True

    class OpExpression(object):
        def is_const(self, config):
            for leaf in self.leaves:
                if leaf.is_const(config) is False:
                    return False
            return True

    class Identifier(object):
        def is_const(self, config):
            return "const" in self.decl.flags

    class CallExpression(object):
        def is_const(self, config):
            return False