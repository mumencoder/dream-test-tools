
class Evaluate(object):
    class ConstExpression(object):
        def eval(self, config):
            return self.value

    class OpExpression(object):
        def eval(self, config):
            if self.op.display == "+":
                return self.leaves[0].eval(config) + self.leaves[1].eval(config)
            if self.op.display== "-":
                return self.leaves[0].eval(config) - self.leaves[1].eval(config)
            if self.op.display == "*":
                return self.leaves[0].eval(config) * self.leaves[1].eval(config)
            if self.op.display == "/":
                if self.leaves[1].eval(config) in [0, -0, 0.0, -0.0]:
                    raise GenerationError()
                return self.leaves[0].eval(config) / self.leaves[1].eval(config)
            raise Exception("cannot evaluate")

    class Identifier(object):
        def eval(self, config):
            if self.decl.value is None:
                raise GenerationError()
            else:
                return self.decl.value

    class CallExpression(object):
        def eval(self, config):
            return 1