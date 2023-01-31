
from ...common import *
from ...model import *

class BaseBuilder(object):
    stdlib = Stdlib.initialize()

    def __init__(self):
        self.node_info = {}
        self.undefined_vars = []

        self.toplevel = self.initialize_node( AST.Toplevel() )
        for path in self.stdlib.objects.keys():
            node = self.toplevel.tree.add_path( path )
            node.is_stdlib = True


    def initialize_node(self, node):
        self.node_info[node] = {}
        Semantics.init_semantics( node )
        if hasattr(node, 'init_semantics'):
            node.init_semantics()
        return node

    def generate(self, env):
        env = env.branch()
        self.initialize_config()
        env.attr.builder.init_node = self.initialize_node
        #eligible_actions = ["object_declare", "var_declare", "proc_declare", "var_define", "add_proc_parameter", "add_proc_stmt"]
        eligible_actions = ["object_declare"]
        self.declare_block_stack = [self.toplevel]

        generating = True
        while generating:
            if len(eligible_actions) == 0:
                break

            action = random.choice( eligible_actions )
            env.attr.action = action

            if action == "object_declare":
                if self.object_declare_remaining(env) <= 0:
                    eligible_actions.remove( "object_declare" )
                    continue
                self.declare_object(env)
                pops = random.choice( [0,0,0,1,1,1,2,2,3] )
                while pops > 0 and len(self.declare_block_stack) > 1:
                    self.declare_block_stack.pop()

            if action == "var_declare":
                if self.var_declare_remaining(env) <= 0:
                    eligible_actions.remove( "var_declare" )
                    continue
                current_object = self.choose_object(env)
                env.attr.current_object = current_object
                var_declare = self.declare_var(env)
                current_object.add_leaf( var_declare )

            if action == "proc_declare":
                if self.proc_declare_remaining(env) <= 0:
                    eligible_actions.remove( "proc_declare" )
                    continue
                current_object = self.choose_object(env)
                env.attr.current_object = current_object
                proc_declare = self.declare_proc(env)
                current_object.add_leaf( proc_declare )

            if action == "var_define":
                if self.undefined_vars_left(env) is False:
                    if "var_declare" not in eligible_actions:
                        eligible_actions.remove( "var_define" )
                    continue
                current_var = self.choose_undefined_var(env)
                env.attr.current_var = current_var
                if random.random() < self.config.attr.define.var.empty_initializer_prob:
                    pass
                else:
                    expr = self.create_var_expr(env)
                    current_var.set_expression( expr )
                self.undefined_vars.remove( current_var )

            if action == "add_proc_parameter":
                if self.proc_args_left(env) is False:
                    if "proc_declare" not in eligible_actions:
                        eligible_actions.remove( "add_proc_parameter" )
                    continue
                current_proc = self.choose_proc_declare(env)
                env.attr.current_proc = current_proc
                proc_param = self.create_proc_param(env)
                current_proc.add_param( proc_param )
                self.node_info[ current_proc ]["args"] -= 1
                    
            if action == "add_proc_stmt":
                if self.proc_stmts_left(env) is False:
                    if "proc_declare" not in eligible_actions:
                        eligible_actions.remove( "add_proc_stmt" )
                    continue
                current_proc = self.choose_proc_declare(env)
                env.attr.current_proc = current_proc
                proc_stmt = self.create_proc_stmt(env)
                current_proc.add_stmt( proc_stmt )
                self.node_info[ current_proc ]["stmts"] -= 1    