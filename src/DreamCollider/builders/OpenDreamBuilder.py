
# generates code that OpenDream should compile without errors

from .common import *
from ..model import *

from .BaseBuilder import BaseBuilder

class OpenDreamBuilder(BaseBuilder):
    def get_action_phases(self):
        return ["phase1"]
    
    def actions_phase1(self):
        action = Object.RandomStackWalkObjectDeclareAction( self.toplevel ) 

        opg = Object.ObjectPathGenerator()
        opg.config.set("obj.path.extend_path_prob", 0.5)
        opg.config.set_choice("obj.path.prefix_type", absolute=1, upwards=0, downwards=0, relative=99)
        opg.config.set_choice("obj.path.extend_type", leaf=100, upwards=0, downwards=0)
        action.generate_object_path = opg

        Action.counted( action, max(1, round( random.gauss(12, 6))) )
        self.eligible_actions.append( action )

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=0, indent=11, nice_bracket=0)
