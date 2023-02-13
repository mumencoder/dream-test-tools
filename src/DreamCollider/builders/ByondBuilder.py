
# generates code that DreamMaker should compile without errors

from .common import *
from ..model import *

class ByondBuilder(
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
        config.set_choice("obj.path.prefix_type", absolute=1, upwards=4, downwards=4, relative=8)
        config.set_choice("obj.path.extend_type", leaf=8, upwards=1, downwards=1)
        config.set("obj.path.allowed_stdlib_types", list( self.stdlib.objects.keys() ) )

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=2, indent=11, nice_bracket=11)
