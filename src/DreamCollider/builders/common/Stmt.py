
from ...common import *

from ...Tree import *

class RandomStmt(object):
    def config_stmt(self, config):
        config.set_choice("stmt.type", output=1)
        config.set_choice("stmt.type.output", normal=5, irregular=1)

    def print_here_stmt(self, env):
        return AST.Stmt.Expression.new( 
            expr=AST.Op.ShiftLeft.new( 
                exprs=[ 
                    AST.Expr.Identifier.new(name="world"), 
                    AST.TextNode.new(text='"[.....]"')]
            )
        )

    def create_proc_stmt(self, env):
        stmt_type = self.choose_option( self.config.attr.define.proc.stmt.choices.type )

        if stmt_type == "output_normal":
            stmt = AST.Stmt.Expression.new(
                expr=AST.Op.ShiftLeft.new(
                    exprs=[
                        AST.Expr.Identifier.new(name = "world"), self.create_var_expr(env),
                        self.create_var_expr(env)
                    ]
                )
            )
        elif stmt_type == "output_here":
            stmt = self.print_here_stmt(env)
        elif stmt_type == "output_irregular":
            stmt = AST.Stmt.Expression.new(
                expr=AST.Op.ShiftLeft.new(
                    exprs=[
                        self.create_var_expr(env),
                        self.create_var_expr(env)
                    ]
                )
            )
        else:
            raise Exception("unknown stmt option")

        return stmt