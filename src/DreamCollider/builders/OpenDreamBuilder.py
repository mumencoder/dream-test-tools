
# generates code that OpenDream should compile without errors

from .common import *
from ..model import *

class OpenDreamBuilder(
        BaseBuilder.BaseBuilder,
        Object.RandomObjects,
        Proc.RandomProcs,
        Proc.SimpleProcCreator,
        Stmt.RandomStmt,
        Expr.RandomExprGenerator,
        Var.RandomVars,
        DefaultConfig.DefaultConfig):

    def config_actions(self, config):
        self.eligible_actions.append( Object.BlockDeclareAction( self.toplevel, "phase1_obj" ) )

    def config_object_paths(self, config):
        config.set("obj.path.flip_override_prob", 0)
        config.set("obj.path.op_extend", 0.5)
        config.set_choice("obj.path.prefix_type", absolute=1, upwards=0, downwards=0, relative=99)
        config.set_choice("obj.path.extend_type", leaf=100, upwards=0, downwards=0)
        config.set("obj.path.allowed_stdlib_types", list( self.stdlib.objects.keys() ) )

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=0, indent=11, nice_bracket=0)
