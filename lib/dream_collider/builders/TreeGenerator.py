
from ..common import *
from ..model import *

import Shared

from .BaseGenerators import *

class TreeGenerator(BaseGenerator, RandomBlocks, RandomVars, RandomProcs, SimpleVarExprCreator, SimpleProcCreator):
    def __init__(self):
        super().__init__()

    def test_string(self, env):
        self.generate( env )
        env.attr.visit.depth = 0
        for node in AST.walk_subtree( self.toplevel ):
            node.ws = collections.deque( default_ws_types[type(node)](node) )
        upar = Unparser()
        upar.convert_block_ws = upar.block_mode_newline
        self.toplevel.unparse(upar)
        AST.print( self.toplevel, sys.stdout, seen=set() )
        print( upar.s.getvalue() )
        return upar.s.getvalue()