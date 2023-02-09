
from ...common import *
from ...model import *

class VarDeclareAction(object):
    def __init__(self, object_tag, var_tags):
        self.var_count = max(0, random.gauss(10, 5))
        self.current_vars = set()
        self.choose_object = self.default_choose_object
        self.generate_var_path = self.default_generate_var_path
        self.generate_var_name = self.default_generate_var_name
        self.object_tag = object_tag
        self.var_tags = var_tags

    def finished(self, env):
        if self.var_count - len(self.current_vars) <= 0:
            return True
        return False

    def default_generate_var_path(self, env):
        return tuple()

    def default_generate_var_name(self, env):
        name = None
        while name is None:
            letters = random.randint(2,3)
            vn = ""
            for i in range(0, letters):
                vn += random.choice(string.ascii_lowercase)
            if vn not in ["as", "to", "in"]:
                name = vn
        return name

    def default_choose_object(self, env):
        choices = env.attr.gen.toplevel.find_tagged(self.object_tag)
        if len(choices) == 0:
            return None
        return random.choice( choices )      

    def __call__(self, env):
        current_object = self.choose_object(env)
        if current_object is None:
            return False
        env.attr.gen.current_object = current_object

        var_declare = env.attr.gen.initialize_node( AST.ObjectVarDefine() )
        env.attr.gen.toplevel.set_tags( var_declare, self.var_tags )
        env.attr.var_declare = var_declare
        var_declare.name = self.generate_var_name( env )
        var_declare.var_path = self.generate_var_path( env )
        self.current_vars.add( var_declare )
        del env.attr.var_declare

        var_declare = self.declare_var(env)
        current_object.add_leaf( var_declare )
        del env.attr.gen.current_object


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

