
from ..common import *
from ..model import *

import Shared

class ExprGenerator:
    terminal_exprs = [AST.Expr.Integer, AST.Expr.Float, AST.Expr.String, AST.Expr.Null]

    def __init__(self):
        pass
        
    def test(self):
        expr = None
        while expr is None:
            try:
                expr = self.expression(Shared.Environment(), depth=2, arity="rval")
                if expr.od_validate() is False:
                    expr = None
            except GenerationError:
                expr = None
        upar = Unparser()
        expr.unparse(upar)
        return f"""
/world/New()
    var/v = {upar.s.getvalue()}
    world.log << "|[v]|"
    world.log << "isnum: [isnum(v)]"
    world.log << "isnull: [isnull(v)]"
    world.log << "ispath: [ispath(v)]"
    text2file("[json_encode(v)]", "test.out.json")
    return json_encode(v)
"""

    def randomString(self, env, lo, hi):
        letters = random.randint(lo,hi)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        return vn

    def expression(self, env, depth=None, arity=None):
        if depth == 1:
            expr = None
            while expr is None:
                expr = self.generate_terminal( arity )
            self.initialize_terminal( env, expr )
            return expr
        else:
            expr = None
            while expr is None:
                expr = self.generate_nonterminal( arity )
            if getattr(expr, 'terminal', None):
                self.initialize_terminal( env, expr )
            if getattr(expr, 'nonterminal', None):
                leaf_arity = expr.arity
                if leaf_arity == "vararg":
                    leaf_arity = random.randint(1,3)*["rval"]
                for arity in leaf_arity:
                    new_depth = random.randint(1, depth-1)
                    expr.exprs.append( self.expression(env, new_depth, arity) )
        return expr

    def initialize_terminal(self, env, expr):
        if type(expr) is AST.Expr.Integer:
            if random.random() < 0.05:
                expr.n = 0
            else:
                expr.n = random.randint(-100,100)
        elif type(expr) is AST.Expr.Float:
            if random.random() < 0.05:
                expr.n = 1 - 2*random.random()
            else:
                expr.n = 100 - 200*random.random()
        elif type(expr) in [AST.Expr.String, AST.Expr.Resource]:
            expr.s = self.randomString(env, 0, 3)
        # TODO: fuzz AST.Expr.Super
        elif type(expr) in [AST.Expr.Self, AST.Expr.Null]:
            pass
        else:
            raise Exception("cannot initialize", type(expr))

    def generate_terminal(self, arity):
        if arity == "rval":
            return random.choice( ExprGenerator.terminal_exprs )()
        elif arity == "lval":
            raise GenerationError()
        elif arity == "storage":
            raise GenerationError()
        elif arity == "path":
            # TODO: allow paths
            raise GenerationError()
        elif arity == "prop":
            raise GenerationError()
        else:
            raise Exception("unknown arity", arity)

    def generate_nonterminal(self, arity):
        if arity == "rval":
            return random.choice( AST.nonterminal_exprs )()
        elif arity == "lval":
            raise GenerationError()
        elif arity == "storage":
            raise GenerationError()
        elif arity == "path":
            # TODO: allow paths
            raise GenerationError()
        elif arity == "prop":
            raise GenerationError()
        else:
            raise Exception("unknown arity", arity)