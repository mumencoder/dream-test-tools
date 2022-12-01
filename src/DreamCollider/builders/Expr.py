
from ..common import *
from ..model import *

from . import Names

class GenerationError(Exception):
    pass

class SimpleVarExprCreator(object):
    def create_var_expr(self, env, var_define):
        expr = AST.Expr.Integer()
        expr.n = random.randint(-100,100)
        return expr

class RandomExprGenerator(object):
    def create_var_expr(self, env, var_define):
        expr = None
        while expr is None:
            try:
                expr = self.expression( env, env.attr.expr.depth, "rval" )
            except GenerationError:
                pass
        return expr

    def expression(self, env, depth=None, arity=None):
        if depth == 1:
            expr = None
            while expr is None:
                expr = self.generate_terminal( arity )
        else:
            expr = None
            while expr is None:
                expr = self.generate_nonterminal( arity )
                leaf_arity = expr.arity
                if leaf_arity == "vararg":
                    leaf_arity = random.randint(1,3)*["rval"]
                for arity in leaf_arity:
                    new_depth = random.randint(1, depth-1)
                    expr.exprs.append( self.expression(env, new_depth, arity) )
        return expr

    def generate_terminal(self, arity):
        if arity == "rval":
            expr = random.choice( [AST.Expr.Integer, AST.Expr.Float, AST.Expr.String, AST.Expr.Null] )()
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
                expr.s = Names.randomString(0, 3)
            # TODO: fuzz AST.Expr.Super
            elif type(expr) in [AST.Expr.Self, AST.Expr.Null]:
                pass
            else:
                raise Exception("cannot initialize", type(expr))
            return expr
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