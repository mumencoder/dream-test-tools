
from . import Toplevel
from . import Object
from . import Proc
from . import Expr
from . import Var
from . import DefaultConfig

from ..model import *

class FullRandomBuilder(
        Toplevel.Toplevel,
        Object.RandomObjects,
        Proc.RandomProcs,
        Proc.SimpleProcCreator,
        Expr.RandomExprGenerator,
        Var.RandomVars,
        DefaultConfig.DefaultConfig):
    def __init__(self):
        self.stdlib = Stdlib.initialize()
        self.toplevel = self.initialize_node( AST.Toplevel() )

        self.initialize_config()

        self.proc_defines = {}
        self.var_defines = []
        self.user_object_blocks = []

    def initialize_node(self, node):
        Semantics.init_semantics( node )
        if hasattr(node, 'init_semantics'):
            node.init_semantics()
        return node

    def generate(self, env):
        eligible_actions = ["object_declare", "var_declare", "proc_declare", "var_define", "add_proc_parameter", "add_proc_stmt"]

        generating = True
        while generating:
            if len(eligible_actions) == 0:
                break

            action = random.choice( eligible_actions )
            env.attr.action = action

            if action == "object_declare":
                if self.object_declare_count(env) <= 0:
                    eligible_actions.remove( "object_declare" )
                    continue
                self.declare_object(env)

            if action == "var_declare":
                if self.var_declare_count(env) <= 0:
                    eligible_actions.remove( "var_declare" )
                    continue
                current_object = self.choose_object(env)
                var_declare = self.declare_var(env, current_object)
                current_object.add_leaf( var_declare )

            if action == "proc_declare":
                if self.proc_declare_count(env) <= 0:
                    eligible_actions.remove( "proc_declare" )
                    continue
                current_object = self.choose_object(env)
                proc_declare = self.declare_proc(env, current_object)
                current_object.add_leaf( proc_declare )

            if action == "var_define":
                if self.undefined_vars_left(env) is False:
                    if "var_declare" not in eligible_actions:
                        eligible_actions.remove( "var_define" )
                    continue
                current_var = self.choose_undefined_var(env)
                expr = self.create_var_expr(env, current_var)
                current_var.set_expression( expr )
                self.var_defines.remove( current_var )

            if action == "add_proc_parameter":
                if self.proc_args_left(env) is False:
                    if "proc_declare" not in eligible_actions:
                        eligible_actions.remove( "add_proc_parameter" )
                    continue
                current_proc = self.choose_proc_declare(env)
                proc_param = self.create_proc_param(env, current_proc)
                current_proc.add_param( proc_param )
                self.proc_defines[ current_proc ]["args"] -= 1
                    
            if action == "add_proc_stmt":
                if self.proc_stmts_left(env) is False:
                    if "proc_declare" not in eligible_actions:
                        eligible_actions.remove( "add_proc_stmt" )
                    continue
                current_proc = self.choose_proc_declare(env)
                proc_stmt = self.create_proc_stmt(env, current_proc)
                current_proc.add_stmt( proc_stmt )
                self.proc_defines[ current_proc ]["stmts"] -= 1


