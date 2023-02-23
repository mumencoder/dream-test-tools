
from ...common import *

from ...Tree import *
from . import Var


class RandomStmt(object):
    def config_stmt(self, config):
        config.set_choice("stmt.type", expr=1, var_define=10, output_normal=10, output_here=1, output_irregular=1)

    def print_here_stmt(self, env):
        return AST.Stmt.Expression.new( 
            expr=AST.Op.ShiftLeft.new( 
                exprs=[ 
                    AST.Expr.Identifier.new(name="world"), 
                    AST.TextNode.new(text='"[.....]"')]
            )
        )

    def create_proc_stmt(self, env):
        stmt_type = self.choose_option( "stmt.type" )

        match stmt_type:
            case "expr":
                stmt = AST.Stmt.Expression.new( expr=self.create_var_expr(env) )
            case "var_define":
                stmt = AST.Stmt.VarDefine.new( 
                    name=Var.RandomVarName(env, self),
                    var_type=Var.RandomVarMod(env, self),
                    expr=self.create_var_expr(env)
                )
            case "output_normal":
                stmt = AST.Stmt.Expression.new(
                    expr=AST.Op.ShiftLeft.new(
                        exprs=[
                            AST.Expr.Identifier.new(name = "world"), self.create_var_expr(env),
                            self.create_var_expr(env)
                        ]
                    )
                )
            case "output_here":
                stmt = self.print_here_stmt(env)
            case "output_irregular":
                stmt = AST.Stmt.Expression.new(
                    expr=AST.Op.ShiftLeft.new(
                        exprs=[
                            self.create_var_expr(env),
                            self.create_var_expr(env)
                        ]
                    )
                )
            case _:
                raise Exception("unknown stmt option")

        return stmt