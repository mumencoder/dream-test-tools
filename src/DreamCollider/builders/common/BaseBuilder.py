
from ...common import *
from ...model import *

class BaseBuilder(object):
    stdlib = Stdlib.initialize()

    def __init__(self):
        self.config = ColliderConfig()
        self.node_info = {}
        self.undefined_vars = set()
        self.undefined_procs = set()
        self.eligible_actions = []
        self.tags = Tags()
        self.action_fails = collections.defaultdict(int)

        self.initialize_toplevel()

        self.initialize_config()

    def initialize_config(self):
        self.config = ColliderConfig()
        
        for name in dir(self):
            if name.startswith('config_'):
                config_fn = getattr(self, name)
                if hasattr(config_fn, '__call__'):
                    config_fn(self.config)
                    
    def initialize_toplevel(self):
        self.toplevel = self.initialize_node( AST.Toplevel.new() )
        self.toplevel.stdlib = self.stdlib
        for path in self.stdlib.objects.keys():
            node = self.toplevel.tree.add_path( path )
            node.is_stdlib = True

    def initialize_node(self, node):
        self.node_info[node] = {}
        Semantics.init_semantics( node )
        if hasattr(node, 'init_semantics'):
            node.init_semantics()
        return node

    def build_all(self, env):
        env = env.branch()
        action_count = 0
        for phase in self.get_action_phases():
            getattr(self, f'actions_{phase}')(env)
            while len( self.eligible_actions ) != 0:
                self.next_action(env)
                if action_count > 10000:
                    raise Exception("too many attempts")
                action_count += 1

    def next_action(self, env):
        action = random.choice(self.eligible_actions)
        if action.finished(env):
            self.eligible_actions.remove( action )
        else:
            result = action(env)
            if result is None:
                self.action_fails[action] += 1
            if self.action_fails[action] >= 128:
                self.eligible_actions.remove( action )