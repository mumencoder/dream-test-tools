
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
        # declaration will not express a semantically correct override
        config.declare_param("obj.path.flip_override_prob")

        # path will be extended
        config.declare_param("obj.path.extend_prob")

        # list of types in tuple form that can show up as ObjectBlocks
        config.declare_param("obj.path.allowed_stdlib_types")