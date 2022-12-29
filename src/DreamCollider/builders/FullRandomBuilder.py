
from . import Toplevel
from . import Object
from . import Proc
from . import Expr
from . import Var

from ..model import *

class FullRandomBuilder(
        Toplevel.Toplevel,
        Object.RandomBlocks,
        Proc.RandomProcs, 
        Proc.SimpleProcCreator,
        Expr.RandomExprGenerator,
        Var.RandomVars):
    pass

    def initialize_node(self, node):
        Semantics.init_semantics( node )
        if hasattr(node, 'init_semantics'):
            node.init_semantics()
        return node
