
from ...common import *

from ...Tree import *

class RandomStmt(object):
    def config_stmt(self, config):
        # "world << expr"
        config.attr.define.proc.stmt.weights.type.output_normal = 5
        # "expr << expr"
        config.attr.define.proc.stmt.weights.type.output_irregular = 1

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