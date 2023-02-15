
# generates code that uses every feature available in the most random manner

from .common import *
from ..model import *

class FullRandomBuilder(
        BaseBuilder.BaseBuilder,
        Proc.RandomProcs,
        Proc.SimpleProcCreator,
        Stmt.RandomStmt,
        Expr.RandomExprGenerator,
        Var.RandomVars,
        DefaultConfig.DefaultConfig):

    pass