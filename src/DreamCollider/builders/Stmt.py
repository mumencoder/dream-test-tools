
from ..common import *

from ..Tree import *

class RandomStmt(object):
    def create_proc_stmt(self, env):
        stmt_type = self.choose_option( self.config.attr.define.proc.stmt.choices.type )

        if stmt_type == "output_normal":
            stmt = AST.create( env, (AST.Stmt.Expression, 
                {"expr":(AST.Op.ShiftLeft,
                    {"exprs":[
                        (AST.Expr.Identifier, {"name":"world"}),
                        self.create_var_expr(env)
                    ]}
                )} 
            ))
        elif stmt_type == "output_irregular":
            stmt = AST.create( env, (AST.Stmt.Expression, 
                {"expr":(AST.Op.ShiftLeft,
                    {"exprs":[
                        self.create_var_expr(env),
                        self.create_var_expr(env)
                    ]}
                )} 
            ))
        else:
            raise Exception("unknown stmt option")

        return stmt