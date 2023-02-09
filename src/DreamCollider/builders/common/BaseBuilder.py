
from ...common import *
from ...model import *

class BaseBuilder(object):
    stdlib = Stdlib.initialize()

    def __init__(self):
        self.node_info = {}
        self.undefined_vars = []
        self.eligible_actions = []
        self.tags = Tags()

        self.toplevel = self.initialize_node( AST.Toplevel() )
        for path in self.stdlib.objects.keys():
            node = self.toplevel.tree.add_path( path )
            node.is_stdlib = True
        self.initialize_config()

    def initialize_node(self, node):
        self.node_info[node] = {}
        Semantics.init_semantics( node )
        if hasattr(node, 'init_semantics'):
            node.init_semantics()
        return node

    def build_all(self, env):
        env.attr.builder = self
        while len( self.eligible_actions ) != 0:
            self.next_action(env)

    def next_action(self, env):
        action = random.choice(self.eligible_actions)
        if action.finished(env):
            self.eligible_actions.remove( action )
        else:
            action(env)