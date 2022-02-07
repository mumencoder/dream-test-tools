
from ..common import *

class ConstExpression(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def print(self, parent_op=None):
        return str(self)

    def is_const(self, config):
        return True

    def simplify(self, config):
        return self

    def eval(self, config):
        return self.value

class OpExpression(object):
    def __init__(self, op):
        self.leaves = []
        self.op = op

    def __str__(self):
        return self.print()

    def print(self, parent_op=None):
        display = ""
        if parent_op and parent_op.prec >= self.op.prec:
            display += "("

        cleaf = 0
        for e in self.op.fixity:
            if e == "_":
                display += self.leaves[cleaf].print(parent_op=self.op)
                cleaf += 1
            elif type(e) is str:
                if display == "":
                    display += f"{e}"
                else:
                    display += f" {e} "
            else:
                raise Exception("bad fixity")

        if parent_op and parent_op.prec >= self.op.prec:
            display += ")"
        return display

    def is_const(self, config):
        for leaf in self.leaves:
            if leaf.is_const(config) is False:
                return False
        return True

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
    def __init__(self, decl):
        self.decl = decl

    def __str__(self):
        return self.decl.name

    def print(self, parent_op=None):
        return str(self)

    def is_const(self, config):
        return "const" in self.decl.flags

    def simplify(self, config):
        return self

    def eval(self, config):
        if self.decl.value is None:
            raise GenerationError()
        else:
            return self.decl.value

class CallExpression(object):
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __str__(self):
        display = f"{self.name}("
        display += ",".join([str(arg) for arg in self.args])
        display += ")"
        return display

    def print(self, parent_op=None):
        return str(self)

    def is_const(self, config):
        return False

    def simplify(self, config):
        return self

    def eval(self, config):
        return 1