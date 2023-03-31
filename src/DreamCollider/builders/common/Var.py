
from ...common import *
from ...model import *

from .Config import *
from .Build import *
    
class VarDeclareAction(Configurable):
    def __init__(self):
        super().__init__()
        self.choose_object = None
        self.generate_var_path = None
        self.generate_var_name = None

    def __call__(self, env):
        tries = 0
        current_object = None
        while current_object is None and tries < 10:
            current_object = self.choose_object(env)
            if type(current_object) is AST.ObjectBlock and keyword_object_block(current_object.resolved_path):
                current_object = None
            tries += 1
        if tries == 10:
            return None
        env.attr.current_object = current_object

        is_override = self.config.prob('override_prob')
        if is_override:
            var_object = None
        else:
            var_object = env.attr.collider.builder.initialize_node( AST.ObjectBlock.new() )
            var_object.path = AST.ObjectPath.new(segments=tuple(["var"]))

        var_declare = env.attr.collider.builder.initialize_node( AST.ObjectVarDefine() )
        env.attr.var_declare = var_declare
        var_declare.name = self.generate_var_name( env )
        if var_declare.name is None:
            return None
        var_declare.var_path = self.generate_var_path( env )

        if var_object is None:
            current_object.add_leaf( var_declare )
        else:
            current_object.add_leaf( var_object )
            var_object.add_leaf( var_declare )
        env.attr.collider.builder.undefined_vars.add( var_declare )
        del env.attr.var_declare
        del env.attr.current_object
        self.current_count += 1
        return True

class VarDefinitionAction(Configurable):
    def __init__(self):
        super().__init__()
        self.choose_var = None
        self.generate_define = None

    def finished(self, env):
        return len(env.attr.collider.builder.undefined_vars) == 0

    def __call__(self, env):
        tries = 0
        current_var = None
        while current_var is None and tries < 10:
            current_var = self.choose_var(env)
            tries += 1
        if tries == 10:
            return None
        env.attr.current_var = current_var
        if self.config.prob("empty_initializer_prob"):
            pass
        else:
            expr = self.generate_define(env)
            current_var.set_expression( expr )
        env.attr.collider.builder.undefined_vars.remove( current_var )
        return True
    
class RandomVarName(Configurable):
    def __call__(self, env):
        return random.choice( ["a", "b", "c", "d"] )

class RandomVarMod(Configurable):
    def __call__(self, env):
        match self.config.choose_option('var.path_gen_type'):
            case 'static':
                return ['static']
            case 'const':
                return ['const']
            case 'type':
                return random.choice( list(env.attr.builder.toplevel.tree.root.nodes_by_path.keys()) )
            
class RandomStdlibVarName(Configurable):
    def __call__(self, env):
        choices = env.attr.collider.builder.stdlib.vars[ env.attr.current_object.resolved_path ]
        if len(choices) == 0:
            return None
        choice = random.choice( list(choices.keys()) )
        return choice

class RandomUndefinedVar(Configurable):
    def __call__(self, env):
        if len(env.attr.builder.undefined_vars) == 0:
            return None
        else:
            return random.choice( list(env.attr.builder.undefined_vars) )
