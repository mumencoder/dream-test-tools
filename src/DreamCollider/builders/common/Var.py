
from ...common import *
from ...model import *

class VarDeclareAction(object):
    def __init__(self):
        self.config = ColliderConfig()
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

def EmptyVarPath(env, builder):
    return []

def RandomVarName(env, builder):
    name = None
    while name is None:
        letters = random.randint(2,3)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        if vn not in ["as", "to", "in"]:
            name = vn
    return name

def RandomVarMod(env, builder):
    return []
class RandomStdlibVarName(object):
    def __init__(self):
        pass

    def __call__(self, env):
        choices = env.attr.collider.builder.stdlib.vars[ env.attr.current_object.resolved_path ]
        if len(choices) == 0:
            return None
        choice = random.choice( list(choices.keys()) )
        return choice
     
class VarDefinitionAction(object):
    def __init__(self):
        self.config = ColliderConfig()
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
    
def RandomUndefinedVar(env, builder):
    if len(builder.undefined_vars) == 0:
        return None
    else:
        return random.choice( list(builder.undefined_vars) )
