
from ..common import *
from ..model import *

class SimpleWhitespace(object):
    def assign_whitespace(self, env):
        env.attr.visit.depth = 0
        for node in AST.walk_subtree( self.toplevel ):
            node.ws = collections.deque( Unparse.default_ws_types[type(node)](node) )