
class Simplify(object):
    class OpExpression(object):
        def simplify(self, config):
            for i, leaf in enumerate(self.leaves):
                self.leaves[i] = leaf.simplify(config)

            if self.op.display == "/" and self.leaves[1].is_const(config) and self.leaves[1].eval(config) in [0, -0, 0.0, -0.0]:
                raise GenerationError()

            for i, leaf in enumerate(self.leaves):
                if type(leaf) is not ConstExpression:
                    return self

            if self.op.display == "+":
                return ConstExpression(self.leaves[0].value + self.leaves[1].value)
            if self.op.display== "-":
                return ConstExpression(self.leaves[0].value - self.leaves[1].value)
            if self.op.display == "*":
                return ConstExpression(self.leaves[0].value * self.leaves[1].value)
            if self.op.display == "/":
                return ConstExpression(self.leaves[0].value / self.leaves[1].value)
            raise Exception("cannot evaluate")

    class ConstExpression(object):
        def simplify(self, config):
            return self

    class Identifier(object):
        def simplify(self, config):
            return self

    class CallExpression(object):
        def simplify(self, config):
            return self