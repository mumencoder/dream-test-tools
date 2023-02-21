
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