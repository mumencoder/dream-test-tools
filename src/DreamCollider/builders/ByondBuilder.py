
# generates code that DreamMaker should compile without errors

from .common import *
from ..model import *

from .BaseBuilder import *

class ByondBuilder(BaseBuilder):
    def get_action_phases(self):
        return ["phase1"]

    def actions_phase1(self):
        action = Object.RandomStackWalkObjectDeclareAction( self.toplevel ) 

        opg = Object.ObjectPathGenerator()
        opg.config.set("obj.path.extend_path_prob", 0.5)
        opg.config.set_choice("obj.path.prefix_type", absolute=1, upwards=4, downwards=4, relative=8)
        opg.config.set_choice("obj.path.extend_type", leaf=8, upwards=1, downwards=1)
        action.generate_object_path = opg

        Action.counted( action, max(1, round( random.gauss(12, 6))) )
        self.eligible_actions.append( action )

        ###
        action = Proc.ProcDeclareAction()
        action.config.set("override_prob", 0.02)
        action.config.set("verb_prob", 0.50)
        action.choose_object = Object.AnyObjectBlock()
        action.generate_proc_name = Proc.RandomProcName()

        Action.counted( action, max(0, random.gauss(2, 2)) )
        self.eligible_actions.append( action )

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=2, indent=11, nice_bracket=11)