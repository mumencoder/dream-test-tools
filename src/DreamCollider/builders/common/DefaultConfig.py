
from ...common import *

from ...Tree import *

class DefaultConfig(object):
    def initialize_config(self):
        self.config = ColliderConfig()
        
        for name in dir(self):
            if name.startswith('config_'):
                config_fn = getattr(self, name)
                if hasattr(config_fn, '__call__'):
                    config_fn(self.config)

    def config_common(self, config):
    	# total # of object blocks that will be added to AST 
        config.declare_param("obj.object_block_count")

        # probability that a single-leaf declare will be joined with its parent
        config.declare_param("obj.path.block_join_prob")

        # declaration will not express a semantically correct override
        config.declare_param("obj.path.flip_override_prob")

        # path will be extended
        config.declare_param("obj.path.extend_prob")

        # list of types in tuple form that can show up as ObjectBlocks
        config.declare_param("obj.path.allowed_stdlib_types")