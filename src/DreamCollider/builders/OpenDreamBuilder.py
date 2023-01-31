
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

    def config_object_paths(self, config):
        config.attr.obj.choices.op_extend.leaf = 1
        config.attr.obj.choices.op_extend.upwards = 0
        config.attr.obj.choices.op_extend.downwards = 0

        config.attr.obj.choices.path_prefix.absolute = 1
        config.attr.obj.choices.path_prefix.upwards = 0
        config.attr.obj.choices.path_prefix.downwards = 0
        config.attr.obj.choices.path_prefix.relative = 9
        # which stdlib types can show up as an object block
        config.attr.obj.allowed_stdlib_types = list( self.stdlib.objects.keys() )      