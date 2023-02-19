
# generates code that DreamMaker should compile without errors

from .common import *
from ..model import *

class ByondBuilder(
        BaseBuilder.BaseBuilder,
        Proc.RandomProcs,
        Proc.SimpleProcCreator,
        Stmt.RandomStmt,
        Expr.RandomExprGenerator,
        Var.RandomVars,
        DefaultConfig.DefaultConfig):

    def config_actions(self, config):
        ### RandomObjectDeclareAction
        action = Object.RandomObjectDeclareAction( self.toplevel, "phase1_obj" ) 

        opg = Object.ObjectPathGenerator(self, config)
        opg.config.set("obj.path.extend_path_prob", 0.5)
        opg.config.set_choice("obj.path.prefix_type", absolute=1, upwards=4, downwards=4, relative=8)
        opg.config.set_choice("obj.path.extend_type", leaf=8, upwards=1, downwards=1)
        action.generate_object_path = opg

        Action.counted( action, max(1, round( random.gauss(12, 6))) )
        self.eligible_actions.append( action )

        ### ProcDeclareAction 
        action = Proc.ProcDeclareAction(self)
        action.choose_object = lambda env: random.choice( Object.AnyObjectBlock(env, self) )
        action.generate_proc_name = Proc.RandomProcName()

        Action.counted( action, max(0, random.gauss(2, 2)) )
        self.eligible_actions.append( action )

    def config_object_paths(self, config):
        config.set("obj.path.flip_override_prob", 0)

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=2, indent=11, nice_bracket=11)

class ByondBuilderExperimental(ByondBuilder):
    def config_extra(self, config):
        ### ToplevelDeclareAction for stdlib
        action = Object.ToplevelDeclareAction( self.toplevel )

        pathc = Object.ObjectPathChooser( list( self.stdlib.objects.keys() ) )
        action.choose_path = pathc
        Action.counted( action, max(1, round( random.gauss(4, 2))) )
        self.eligible_actions.append( action )

        ### ProcDelcareAction for stdlib
        action = Proc.ProcDeclareAction(self)
        action.choose_object = lambda env: random.choice( Object.AnyStdlibObjectBlock(env, self) )
        action.generate_proc_name = Proc.RandomStdlibProcName()
        Action.counted( action, max(0, random.gauss(2,2)))
        self.eligible_actions.append( action )
