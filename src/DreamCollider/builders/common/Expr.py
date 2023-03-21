
from ...common import *
from ...model import *
from .Errors import *

class SimpleVarExprCreator(object):
    def create_var_expr(self, env):
        expr = self.initialize_node( AST.Expr.Integer() )
        expr.n = random.randint(-100,100)
        return expr

class RandomExprGenerator(object):
    def create_var_expr(self, env):
        expr = self.expression( env, self.config.get('expr.depth'), "rval" )
        return expr

    def create_call_expression(self, env, depth):
        expr = None
        while expr is None:
            node_cls = random.choice( AST.trait_index["callable"] )
            expr = node_cls()
            expr = self.initialize_node( node_cls() )
            expr = self.initialize_expression( env, expr, depth )
            if expr is None and depth > 1:
                depth -= 1
        return expr

    def randomString(self, lo, hi):
        letters = random.randint(lo,hi)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        return vn

    def randomDMValueType(self):
        return random.choice( [
            "anything", "null", "text",
            "obj", "mob", "turf", "num", "message", "area", 
            "color", "file", "commandtext", "sound", "icon"
        ] )

    def expression(self, env, depth=None, arity=None):
        if depth < 1:
            raise Exception("Invalid depth")
        expr = None
        while expr is None:
            expr = None
            node_cls = random.choice( AST.trait_index[arity] )
            expr = self.initialize_node( node_cls() )
            expr = self.initialize_expression( env, expr, depth )
            if expr is None and depth > 1:
                depth -= 1
        return expr

    def config_expr(self, config):
        config.set("expr.param.is_named", 0.1)
        config.set("expr.depth", 3)

    def initialize_expression(self, env, expr, depth):
        if type(expr) is AST.Expr.Property:
            expr.name = random.choice( ['pa', 'pb', 'pc'] )
            return expr

        if "terminal" not in expr.traits and "nonterminal" not in expr.traits:
            raise Exception("cannot determine depth limit", type(expr))

        if depth == 1:
            if "terminal" not in expr.traits:
                return None
        else:
            if "nonterminal" not in expr.traits:
                return None

        if expr is None:
            pass
        elif "expr" not in expr.traits:
            expr = None
        # no good way to initialize these
        elif type(expr) is AST.Expr.Resource:
            expr = None
        # just fine the way they are
        elif type(expr) in [AST.Expr.Super, AST.Expr.Null, AST.Expr.Self]:
            pass
        elif depth > 1 and hasattr(expr, 'arity'):
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
            # 3.4e38 largest
            # 1.4e-45 smallest
            if random.random() < 0.05:
                expr.n = 1 - 2*random.random()
            else:
                expr.n = 100 - 200*random.random()
        elif type(expr) is AST.Expr.String:
            expr.s = self.randomString(0, 3)
        elif type(expr) is AST.Expr.FormatString:
            for i in range( 0, random.randint(1, 3) ):
                expr.strings.append( self.randomString(0, 3) )
                expr.exprs.append( self.expression(env, depth-1, "rval") )
            expr.strings.append( self.randomString(0, 3) )
        elif type(expr) is AST.Expr.GlobalIdentifier:
            expr.name = random.choice( ['ga', 'gb', 'gc'] )
        elif type(expr) is AST.Expr.Identifier:
            expr.name = random.choice( ['a', 'b', 'c', 'usr'] )
        elif type(expr) is AST.Expr.Path:
            expr.segments = ["/"]
        elif type(expr) is AST.Expr.Call:
            expr.expr = self.create_call_expression(env, random.randint(1, 3) )
            for i in range( 0, random.randint(1,3) ):
                param = AST.Expr.Call.Param()
                if random.random() < self.config.prob('expr.param.is_named'):
                    param.name = self.randomString(0, 3)
                param.value = self.expression(env, depth-1, "rval")
                expr.args.append( param )
        elif type(expr) is AST.Expr.Input:
            for i in range( 0, random.randint(1,3) ):
                param = AST.Expr.Call.Param()
                if random.random() < self.config.prob('expr.param.is_named'):
                    param.name = self.randomString(0, 3)
                param.value = self.expression(env, depth-1, "rval")
                expr.args.append( param )
            expr.as_type = self.randomDMValueType()
            expr.in_list = self.expression(env, depth-1, "rval")
        elif type(expr) is AST.Expr.New:
            for i in range( 0, random.randint(1,3) ):
                param = AST.Expr.Call.Param()
                if random.random() < self.config.prob('expr.param.is_named'):
                    param.name = self.randomString(0, 3)
                param.value = self.expression(env, depth-1, "rval")
                expr.args.append( param )
        elif type(expr) is AST.Expr.ModifiedType:
            expr.path = self.expression(env, 1, "path")
            for i in range( 0, random.randint(1,3) ):
                mod = AST.Expr.ModifiedType.Mod()
                mod.var = self.randomString(0, 3)
                mod.val = self.expression(env, depth-1, "rval")
                expr.mods.append( mod )
        elif type(expr) is AST.Expr.Pick:
            for i in range( 0, random.randint(1,3) ):
                entry = AST.Expr.Pick.Entry()
                entry.p = self.expression(env, 1, "numeric")
                entry.val = self.expression(env, depth-1, "rval")
                expr.options.append( entry )
        elif type(expr) is AST.Expr.AsType:
            expr.value = self.randomDMValueType()
        else:
            raise Exception("cannot initialize", type(expr))
        return expr

