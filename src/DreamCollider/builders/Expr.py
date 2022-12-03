
from ..common import *
from ..model import *

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

    def randomString(self, lo, hi):
        letters = random.randint(lo,hi)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        return vn

    def expression(self, env, depth=None, arity=None):
        tries = 0
        expr = None
        while expr is None:
            if tries > 5:
                raise GenerationError()

            if arity == "rval":
                if depth == 1:
                    expr = random.choice( AST.terminal_exprs )()
                else:
                    expr = random.choice( AST.nonterminal_exprs )()
            elif arity == "lval":
                expr = AST.Expr.GlobalIdentifier()
            elif arity == "storage":
                expr = AST.Expr.GlobalIdentifier()
            elif arity == "path":
                expr = AST.Expr.Path()
            elif arity == "prop":
                expr = AST.Expr.Property()
            else:
                raise Exception("unknown arity", arity)

            if expr is None:
                pass
            elif expr.stmt_only:
                expr = None
            elif depth > 1 and expr.is_op:
                leaf_arity = expr.arity
                if leaf_arity == "vararg":
                    leaf_arity = random.randint(1,3)*["rval"]
                for arity in leaf_arity:
                    new_depth = random.randint(1, depth-1)
                    expr.add_expr( self.expression(env, new_depth, arity) )
            elif type(expr) is AST.Expr.Integer:
                if random.random() < 0.05:
                    expr.n = 0
                else:
                    expr.n = random.randint(-100,100)
            elif type(expr) is AST.Expr.Float:
                if random.random() < 0.05:
                    expr.n = 1 - 2*random.random()
                else:
                    expr.n = 100 - 200*random.random()
            elif type(expr) is AST.Expr.Resource:
                expr = None
            elif type(expr) is AST.Expr.String:
                expr.s = self.randomString(0, 3)
            elif type(expr) is AST.Expr.GlobalIdentifier:
                expr.name = random.choice( ['a', 'b', 'c'] )
            elif type(expr) is AST.Expr.Identifier:
                expr.name = random.choice( ['a', 'b', 'c'] )
            elif type(expr) is AST.Expr.Property:
                expr.name = random.choice( ['a', 'b', 'c'] )
            elif type(expr) is AST.Expr.Path:
                expr = self.random_path()
            elif type(expr) in [AST.Expr.Null, AST.Expr.Super, AST.Expr.Self]:
                pass
            elif type(expr) in [AST.Expr.FormatString, AST.Expr.Call.Expr, AST.Expr.Call.Identifier]:
                # TODO: things that could be initialized
                expr = None
            else:
                raise Exception("cannot initialize", type(expr))

            tries += 1

        return expr