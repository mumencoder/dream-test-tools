
import random

from . import *
from ..model import *

class ConstExprBuilder(object):
    def __init__(self):
        self.ops = ["+", "-", "*", "/"]

    def expr(self, config, depth=None):
        if depth == 1:
            return DefaultBuilder.const_int(config)
        else:
            expr = None
            while expr is None:
                try:
                    op = config['model'].get_op(random.choice(self.ops))
                    e = OpExpression(op)
                    e.op = op
                    for place in op.arity:
                        new_depth = random.randint(1, depth-1)
                        e.leaves.append( self.expr(config, new_depth) )
                    expr = e
                except GenerationError:
                    pass
            return expr
