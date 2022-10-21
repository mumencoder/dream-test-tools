
from ..common import *
from ..model import *

import Shared

class FullGenerator(object):
    def __init__(self):
        pass

    def generate(self, env):
        env.attr.gen.splits = random.randint(1, 8)
        env.attr.gen.vars = random.randint(0, env.attr.gen.splits*2 + 2)
        env.attr.gen.procs = random.randint(0, int(env.attr.gen.splits/2) + 2)

        env.attr.gen.object_block_names = ['datum', 'atom', 'area', 'turf', 'obj', 'mob', 'ty1', 'ty2', 'ty3', 'ob_only']
        tl_node = AST.Toplevel()

        env.attr.gen.blocks = [tl_node]
        while env.attr.gen.splits > 0:
            split_block = random.choice( env.attr.gen.blocks )
            ob_node = AST.ObjectBlock()
            env.attr.gen.blocks.append( ob_node )
            ob_node.name = random.choice( env.attr.gen.object_block_names )
            split_block.add_leaf( ob_node )
            env.attr.gen.splits -= 1

        for ob_node in env.attr.gen.blocks:
            self.ObjectBlock(env, ob_node)

        env.attr.gen.var_decls = []
        for i in range(0, env.attr.gen.vars):
            block = random.choice( env.attr.gen.blocks )
            var_decl = None
            while var_decl is None:
                var_decl = self.VarDefine(env, block)
                if var_decl.validate_name() is False:
                    var_decl = None
            block.add_leaf( var_decl )
            env.attr.gen.var_decls.append( var_decl )

        for var_decl in env.attr.gen.var_decls:
                expr = None
                while expr is None:
                    try:
                        expr = self.expression(env, var_decl, depth=5, arity="rval")
                        expr.simplify(var_decl.block)
                        if not expr.is_const(var_decl) and var_decl.initialization_mode() == "const":
                            expr = None
                        elif var_decl.validate_expression( expr ) is False:
                            expr = None
                        else:
                            var_decl.set_expression( expr )
                    except GenerationError:
                        expr = None

        return tl_node

    def ObjectBlock(self, env, node):
        pass

    def VarDefine(self, env, block):
        if type(block) is AST.Toplevel:
            return self.GlobalVarDefine(env, block)
        elif type(block) is AST.ObjectBlock:
            return self.ObjectVarDefine(env, block)
        else:
            raise Exception("bad block")

    def ProcDefine(self, env, block):
        if type(block) is AST.Toplevel:
            return self.GlobalProcDefine(env, block)
        elif type(block) is AST.ObjectBlock:
            return self.ObjectProcDefine(env, block)
        else:
            raise Exception("bad block")

    def GlobalVarDefine(self, env, block):
        node = AST.GlobalVarDefine()
        node.name = self.randomVarName(env)
        node.scope = block
        return node

    def ObjectVarDefine(env, block):
        node = AST.ObjectVarDefine()   
        node.name = self.randomVarName(env)    
        node.scope = block
        return node

    def GlobalProcDefine(self, env, block):
        node = AST.GlobalProcDefine()
        node.name = self.procName(env)
        node.body = self.Statements(env, count=5)
        node.scope = block
        return node

    def ObjectProcDefine(self, env, block):
        node = AST.ObjectProcDefine()
        node.name = self.procName(env)
        node.body = self.Statements(env, count=5)
        node.scope = block
        return node

    def randomVarName(self, env):
        letters = random.randint(2,3)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        return vn

    def randomString(self, env, lo, hi):
        letters = random.randint(lo,hi)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        return vn

    def expression(self, env, var_decl, depth=None, arity=None):
        if depth == 1:
            expr = None
            while expr is None:
                expr = self.generate_terminal( var_decl, arity )
            self.initialize_terminal( env, var_decl, expr )
            return expr
        else:
            expr = None
            while expr is None:
                expr = self.generate_nonterminal( var_decl, arity )
            if getattr(expr, 'terminal', None):
                self.initialize_terminal( env, var_decl, expr )
            if getattr(expr, 'nonterminal', None):
                leaf_arity = expr.arity
                if leaf_arity == "vararg":
                    leaf_arity = random.randint(1,3)*["rval"]
                for arity in leaf_arity:
                    new_depth = random.randint(1, depth-1)
                    expr.exprs.append( self.expression(env, var_decl, new_depth, arity) )
        return expr

    def initialize_terminal(self, env, var_decl, expr):
        if type(expr) is AST.Expr.Integer:
            expr.n = random.randint(-100,100)
        elif type(expr) is AST.Expr.Float:
            expr.n = 100 - 200*random.random()
        elif type(expr) in [AST.Expr.Identifier, AST.Expr.GlobalIdentifier]:
            expr.name = self.choose_scoped_identifier(var_decl, expr)
        elif type(expr) in [AST.Expr.String, AST.Expr.Resource]:
            expr.s = self.randomString(env, 0, 6)
        # TODO: fuzz AST.Expr.Super
        elif type(expr) in [AST.Expr.Self, AST.Expr.Null]:
            pass
        else:
            raise Exception("cannot initialize", type(expr))

    def generate_terminal(self, var_decl, arity):
        if arity == "rval":
            return random.choice( AST.terminal_exprs )()
        elif arity == "lval":
            return AST.Expr.Identifier()
        elif arity == "storage":
            return AST.Expr.Identifier()
        elif arity == "path":
            # TODO: allow paths
            raise GenerationError()
        elif arity == "prop":
            raise GenerationError()
        else:
            raise Exception("unknown arity", arity)

    def generate_nonterminal(self, var_decl, arity):
        if arity == "rval":
            return random.choice( AST.nonterminal_exprs )()
        elif arity == "lval":
            return AST.Expr.Identifier()
        elif arity == "storage":
            return AST.Expr.Identifier()
        elif arity == "path":
            # TODO: allow paths
            raise GenerationError()
        elif arity == "prop":
            raise GenerationError()
        else:
            raise Exception("unknown arity", arity)

    def choose_scoped_identifier(self, var_decl, expr):
        if type(var_decl.scope) is AST.Toplevel:
            var_decls = list(var_decl.scope.get_vars())
            if len(var_decls) == 0:
                raise GenerationError()
            var_decl = random.choice( random.choice( var_decls ) )
            return var_decl.name
        elif type(expr) is AST.Expr.GlobalIdentifier:
            var_decls = list(var_decl.scope.root.get_vars())
            if len(var_decls) == 0:
                raise GenerationError()
            var_decl = random.choice( random.choice( var_decls ) )
            return var_decl.name
        elif type(var_decl.scope) is AST.ObjectBlock:
            blocks = var_decl.scope.root.object_blocks_by_path[var_decl.scope.path]
            if len(blocks) == 0:
                raise GenerationError()
            block = random.choice( blocks )
            block = random.choice( list(block.parent_chain()) )
            var_decls = list(var_decl.scope.get_vars()) 
            if len(var_decls) == 0:
                raise GenerationError()
            var_decl = random.choice( random.choice( var_decls ) )
            return var_decl.name
        else:
            raise Exception("bad scope")
