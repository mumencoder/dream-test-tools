
from . import Proc
from . import Tree
from . import Vars
from . import Expr

class FullRandomBuilder(
        Proc.RandomProcs, 
        Proc.SimpleProcCreator,
        Tree.Toplevel,
        Tree.RandomBlocks,
        Vars.RandomVars,
        Expr.RandomExprGenerator):
    pass

    def initialize_node(self, node):
        if hasattr(node, 'init_semantics'):
            node.init_semantics()
        # TODO: Get this in Semantics somewhere
        node.errors = []
        return node
