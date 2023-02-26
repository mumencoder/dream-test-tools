
# generates code that DreamMaker should compile without errors

from .common import *
from ..model import *

class ByondBuilder(
        BaseBuilder.BaseBuilder,
        Proc.SimpleProcCreator,
        Stmt.RandomStmt,
        Expr.RandomExprGenerator,
        DefaultConfig.DefaultConfig):
    
    def get_action_phases(self):
        return ["phase1"]

    def actions_phase1(self, env):
        action = Object.RandomStackWalkObjectDeclareAction( self.toplevel, "phase1_obj" ) 

        opg = Object.ObjectPathGenerator(self)
        opg.config.set("obj.path.extend_path_prob", 0.5)
        opg.config.set_choice("obj.path.prefix_type", absolute=1, upwards=4, downwards=4, relative=8)
        opg.config.set_choice("obj.path.extend_type", leaf=8, upwards=1, downwards=1)
        action.generate_object_path = opg

        Action.counted( action, max(1, round( random.gauss(12, 6))) )
        self.eligible_actions.append( action )

        ###
        action = Proc.ProcDeclareAction(self)
        action.config.set("override_prob", 0.02)
        action.config.set("verb_prob", 0.50)
        action.choose_object = lambda env: safe_choice( Object.AnyObjectBlock(env, self) )
        action.generate_proc_name = Proc.RandomProcName()

        Action.counted( action, max(0, random.gauss(2, 2)) )
        self.eligible_actions.append( action )

    def config_fuzzer(self, config):
        config.set_choice("fuzzer.block_type", oneline=2, indent=11, nice_bracket=11)

class ByondBuilderExperimental(ByondBuilder):
    def get_action_phases(self):
        return ["phase1", "phase2"]

    def actions_phase1(self, env):
        ByondBuilder.actions_phase1(self, env)
        ### ToplevelDeclareAction for stdlib
        action = Object.ToplevelDeclareAction( self.toplevel )

        pathc = Object.ObjectPathChooser( list( self.stdlib.objects.keys() ) )
        action.generate_object_path = pathc
        Action.counted( action, max(1, round( random.gauss(4, 2))) )
        self.eligible_actions.append( action )

        ### ProcDelcareAction for stdlib
        action = Proc.ProcDeclareAction(self)
        action.config.set("override_prob", 0.98)
        action.config.set("verb_prob", 0.05)
        action.choose_object = lambda env: safe_choice( Object.AnyStdlibObjectBlock(env, self) )
        action.generate_proc_name = Proc.RandomStdlibProcName()
        Action.counted( action, max(0, random.gauss(2,2)))
        self.eligible_actions.append( action )

        ###  RandomObjectDeclareAction for stdlib
        action = Object.RandomObjectDeclareAction()
        action.choose_object_block = lambda env: safe_choice( Object.AnyStdlibObjectBlock(env, self) )

        opg = Object.ObjectPathGenerator(self)
        opg.config.set("obj.path.extend_path_prob", 0.02)
        opg.config.set_choice("obj.path.prefix_type", absolute=5, upwards=5, downwards=5, relative=80)
        opg.config.set_choice("obj.path.extend_type", leaf=90, upwards=5, downwards=5)
        action.generate_object_path = opg
    
        Action.counted( action, max(0, random.gauss(2,2)))
        self.eligible_actions.append( action )

        ### VarDeclareAction for user types
        action = Var.VarDeclareAction()
        action.choose_object = lambda env: safe_choice( Object.AnyObjectBlock(env, self) )
        action.config.set("override_prob", 0.02)
        action.generate_var_path = lambda env: Var.EmptyVarPath(env, self)
        action.generate_var_name = lambda env: Var.RandomVarName(env, self)
        Action.counted( action, max(0, random.gauss(4, 4)) )
        self.eligible_actions.append( action )

        ### VarDeclareAction new vars for stdlib types
        action = Var.VarDeclareAction()
        action.choose_object = lambda env: safe_choice( Object.AnyStdlibObjectBlock(env, self) )
        action.config.set("override_prob", 0.02)
        action.generate_var_path = lambda env: Var.EmptyVarPath(env, self)
        action.generate_var_name = lambda env: Var.RandomVarName(env, self)
        Action.counted( action, max(0, random.gauss(4, 4)) )
        self.eligible_actions.append( action )

        ### VarDeclareAction override vars for stdlib types
        action = Var.VarDeclareAction()
        action.choose_object = lambda env: safe_choice( Object.AnyStdlibObjectBlock(env, self) )
        action.config.set("override_prob", 0.98)
        action.generate_var_path = lambda env: Var.EmptyVarPath(env, self)
        action.generate_var_name = Var.RandomStdlibVarName()
        Action.counted( action, max(0, random.gauss(4, 4)) )
        self.eligible_actions.append( action )

    def actions_phase2(self, env): 
        ### VarDefineAction for declared vars
        action = Var.VarDefinitionAction()
        action.config.set("empty_initializer_prob", 0.33)
        action.choose_var = lambda env: Var.RandomUndefinedVar(env, self)
        action.generate_define = lambda env: self.create_var_expr(env)
        self.eligible_actions.append( action )

        ### ProcParameterAction
        action = Proc.ProcParameterAction()
        action.choose_proc = lambda env: Proc.RandomUndefinedProc(env, self)
        action.generate_proc_param = self.create_proc_param
        action.config.set('finalize_proc', 0.20)
        self.eligible_actions.append( action )

        ### ProcStatementAction
        action = Proc.ProcStatementAction()
        action.choose_proc = lambda env: Proc.RandomUndefinedProc(env, self)
        action.generate_proc_stmt = self.create_proc_stmt
        action.config.set('finalize_proc', 0.10)
        self.eligible_actions.append( action )