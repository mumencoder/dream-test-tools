
from ...common import *

from ...Tree import *

class DefaultConfig(object):

    def generate_choices(self, config, pattern):
        filter_pattern = pattern + '.*'
        choice_dict = collections.defaultdict(lambda: collections.defaultdict(list))
        for prop in config.filter_properties(filter_pattern):
            names = prop.split(".")
            option = names[-1]
            wclass = names[-2]
            weight = config.get_attr(prop)
            choice_dict[wclass]["options"].append(option)
            choice_dict[wclass]["weights"].append(weight)

        for wclass, results in choice_dict.items():
            config.set_attr(f"{pattern}.choices.{wclass}", results)

    def choose_option(self, wclass):
        return random.choices( wclass["options"], wclass["weights"] )[0]
        
    def initialize_config(self):
        self.config = Shared.Environment()
        
        for name in dir(self):
            if name.startswith('config_'):
                config_fn = getattr(self, name)
                if hasattr(config_fn, '__call__'):
                    config_fn(self.config)

        self.generate_choices(self.config, '.obj')
        self.generate_choices(self.config, '.define.proc.stmt')
