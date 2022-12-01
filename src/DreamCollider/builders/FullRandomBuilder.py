
from . import Proc
from . import Tree
from . import Vars
from . import Expr
from . import Whitespace

class FullRandomBuilder(
        Proc.RandomProcs, 
        Proc.SimpleProcCreator,
        Tree.Toplevel,
        Tree.RandomBlocks,
        Vars.RandomVars,
        Expr.RandomExprGenerator,
        Whitespace.SimpleWhitespace):
    pass
