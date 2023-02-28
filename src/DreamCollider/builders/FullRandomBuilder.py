
# generates code that uses every feature available in the most random manner

from .common import *
from ..model import *

class FullRandomBuilder(
        BaseBuilder.BaseBuilder,
        Proc.SimpleProcCreator,
        Stmt.RandomStmt,
        Expr.RandomExprGenerator):

    def actions_phase1(self, env):
        pass

    def actions_phase2(self, env):
        pass