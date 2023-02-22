
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
            var_object = env.attr.builder.initialize_node( AST.ObjectBlock.new() )
            var_object.path = AST.ObjectPath.new(segments=tuple(["var"]))

        var_declare = env.attr.builder.initialize_node( AST.ObjectVarDefine() )
        env.attr.var_declare = var_declare
        var_declare.name = self.generate_var_name( env )
        var_declare.var_path = self.generate_var_path( env )

        if var_object is None:
            current_object.add_leaf( var_declare )
        else:
            current_object.add_leaf( var_object )
            var_object.add_leaf( var_declare )
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

class VarDefinitionAction(object):
    def __init__(self, var_declare_tag):
        self.var_declare_tag = var_declare_tag
        self.current_defines = set()
        self.choose_var = self.default_choose_var

    def finished(self, env):
        if self.var_count - len(self.current_vars) <= 0:
            return True
        return False

    def __call__(self, env):
        current_var = self.choose_var(env)
        env.attr.current_var = current_var
        if self.config.prob("vars.empty_initializer_prob"):
            pass
        else:
            expr = self.create_var_expr(env)
            current_var.set_expression( expr )

    def default_choose_var(self, env):
        choices = env.attr.gen.toplevel.find_tagged(self.object_tag, "undefined")
        if len(choices) == 0:
            return None
        choice = random.choice( choices )
        env.attr.gen.remove_tag(choice, "undefined")

class RandomVars(object):
    def config_vars(self, config):
        config.set("vars.empty_initializer_prob", 0.05)

