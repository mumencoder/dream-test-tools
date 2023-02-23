
# generates code that OpenDream should compile without errors

from .common import *
from ..model import *

class OpenDreamBuilder(
        BaseBuilder.BaseBuilder,
        Proc.SimpleProcCreator,
        Stmt.RandomStmt,
        Expr.RandomExprGenerator,
        DefaultConfig.DefaultConfig):

    def actions_phase1(self, env):
        opg = Object.ObjectPathGenerator(self)
        opg.config.set("obj.path.extend_path_prob", 0.5)
        opg.config.set_choice("obj.path.prefix_type", absolute=1, upwards=0, downwards=0, relative=99)
        opg.config.set_choice("obj.path.extend_type", leaf=100, upwards=0, downwards=0)
        action = Object.RandomStackWalkObjectDeclareAction( self.toplevel, "phase1_obj" ) 
        action.generate_object_path = opg
        Action.counted( action, max(1, round( random.gauss(12, 6))) )
        self.eligible_actions.append( action )

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=0, indent=11, nice_bracket=0)
