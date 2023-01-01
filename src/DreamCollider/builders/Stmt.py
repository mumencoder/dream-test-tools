
from ..common import *

from ..Tree import *

class RandomStmt(object):
    def create_proc_stmt(self, env):
        stmt = self.initialize_node( AST.Stmt.Return() )
        stmt.expr = self.initialize_node( AST.Expr.Integer() )
        stmt.expr.n = random.randint(-100, 100)
        return stmt    