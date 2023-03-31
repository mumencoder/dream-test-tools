
from .common import *
from ..model import *

from .BaseBuilder import *
from .ByondBuilder import *

class ByondBuilderExperimental(ByondBuilder):
    def get_action_phases(self):
        return ["phase1", "phase2"]

    def actions_phase1(self):
        ByondBuilder.actions_phase1(self)
        ### ToplevelDeclareAction for stdlib
        action = Object.ToplevelDeclareAction( self.toplevel )

        pathc = Object.ObjectPathChooser( list( self.stdlib.objects.keys() ) )
        action.generate_object_path = pathc
        Action.counted( action, max(1, round( random.gauss(4, 2))) )
        self.eligible_actions.append( action )

        ### ProcDelcareAction for stdlib
        action = Proc.ProcDeclareAction()
        action.config.set("override_prob", 0.98)
        action.config.set("verb_prob", 0.05)
        action.choose_object = Object.AnyStdlibObjectBlock()
        action.generate_proc_name = Proc.RandomStdlibProcName()
        Action.counted( action, max(0, random.gauss(2,2)))
        self.eligible_actions.append( action )

        ###  RandomObjectDeclareAction for stdlib
        action = Object.RandomObjectDeclareAction()
        action.choose_object_block = Object.AnyStdlibObjectBlock()

        opg = Object.ObjectPathGenerator()
        opg.config.set("obj.path.extend_path_prob", 0.02)
        opg.config.set_choice("obj.path.prefix_type", absolute=5, upwards=5, downwards=5, relative=80)
        opg.config.set_choice("obj.path.extend_type", leaf=90, upwards=5, downwards=5)
        action.generate_object_path = opg
    
        Action.counted( action, max(0, random.gauss(2,2)))
        self.eligible_actions.append( action )

        ### VarDeclareAction for user types
        action = Var.VarDeclareAction()
        action.choose_object = Object.AnyObjectBlock()
        action.config.set("override_prob", 0.02)
        action.generate_var_path = Var.RandomVarMod()
        action.generate_var_path.config.set_choice("var.path_gen_type", static=5, const=5, type=5)
        action.generate_var_name = Var.RandomVarName()
        Action.counted( action, max(0, random.gauss(4, 4)) )
        self.eligible_actions.append( action )


        ### VarDeclareAction new vars for stdlib types
        action = Var.VarDeclareAction()
        action.choose_object = Object.AnyStdlibObjectBlock()
        action.config.set("override_prob", 0.02)
        action.generate_var_path = Var.RandomVarMod()
        action.generate_var_path.config.set_choice("var.path_gen_type", static=5, const=5, type=5)
        action.generate_var_name = Var.RandomVarName()
        Action.counted( action, max(0, random.gauss(4, 4)) )
        self.eligible_actions.append( action )

        ### VarDeclareAction override vars for stdlib types
        action = Var.VarDeclareAction()
        action.choose_object = Object.AnyStdlibObjectBlock()
        action.config.set("override_prob", 0.98)
        action.generate_var_path = Var.RandomVarMod()
        action.generate_var_path.config.set_choice("var.path_gen_type", static=5, const=5, type=5)
        action.generate_var_name = Var.RandomStdlibVarName()
        Action.counted( action, max(0, random.gauss(4, 4)) )
        self.eligible_actions.append( action )

    def actions_phase2(self): 
        ### VarDefineAction for declared vars
        action = Var.VarDefinitionAction()
        action.config.set("empty_initializer_prob", 0.33)
        action.choose_var = Var.RandomUndefinedVar()
        action.generate_define = Expr.FullVarExprCreator()
        action.generate_define.generate_dm_valuetype = Expr.RandomDMValue()
        action.generate_define.generate_string = Expr.RandomTextString()     
        action.generate_define.config.set("expr.param.is_named", 0.1)
        action.generate_define.config.set("expr.depth", 3)        
        self.eligible_actions.append( action )

        ### ProcParameterAction
        action = Proc.ProcParameterAction()
        action.config.set('finalize_proc', 0.20)
        action.choose_proc = Proc.RandomUndefinedProc()
        action.generate_proc_param = Proc.RandomProcParam()
        action.generate_proc_param.generate_dm_valuetype = Expr.RandomDMValue()
        action.generate_proc_param.generate_expression = Expr.FullVarExprCreator()
        action.generate_proc_param.generate_expression.generate_dm_valuetype = Expr.RandomDMValue()
        action.generate_proc_param.generate_expression.generate_string = Expr.RandomTextString()     
        action.generate_proc_param.generate_expression.config.set("expr.param.is_named", 0.1)
        action.generate_proc_param.generate_expression.config.set("expr.depth", 3)
        action.generate_proc_param.generate_string = Expr.RandomTextString()
        action.generate_proc_param.config.set('proc.arg.has_path_prob', 0.1)
        action.generate_proc_param.config.set('proc.arg.has_default_prob', 0.1)
        action.generate_proc_param.config.set('proc.arg.has_astype_prob', 0.1)
        self.eligible_actions.append( action )

        ### ProcStatementAction
        action = Proc.ProcStatementAction()
        action.config.set('finalize_proc', 0.10)
        action.choose_proc = Proc.RandomUndefinedProc()
        action.generate_proc_stmt = Stmt.RandomStmt()
        action.generate_proc_stmt.generate_var_name = Var.RandomVarName()
        action.generate_proc_stmt.generate_var_path = Var.RandomVarMod()
        action.generate_proc_stmt.generate_var_path.config.set_choice("var.path_gen_type", static=5, const=5, type=5)
        action.generate_proc_stmt.generate_expression = Expr.FullVarExprCreator()
        action.generate_proc_stmt.generate_expression.generate_dm_valuetype = Expr.RandomDMValue()
        action.generate_proc_stmt.generate_expression.generate_string = Expr.RandomTextString()     
        action.generate_proc_stmt.generate_expression.config.set("expr.param.is_named", 0.1)
        action.generate_proc_stmt.generate_expression.config.set("expr.depth", 3)
        action.generate_proc_stmt.config.set_choice("stmt.type", 
            expr=1, 
            output_normal=10, output_here=1, output_irregular=1,
            var_define=10, 
            _return=2, _break=4, _continue=4, goto=4, label=4,
            _del=10, 
            set=2, 
            spawn=10, 
            _if=10, switch=10,
            _for=10, forenum=10, _while=10, dowhile=10,
            _try=10, throw=10,
        )
        action.generate_string = Expr.RandomTextString()
        self.eligible_actions.append( action )