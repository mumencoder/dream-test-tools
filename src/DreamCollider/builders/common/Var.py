
from ...common import *
from ...model import *

class RandomVars(object):
    def config_vars(self, config):
        config.attr.define.var.empty_initializer_prob = 0.05
        config.attr.define.var.count = max(0, random.gauss(10, 5))
        def var_declare_remaining(self, env):
            return self.config.attr.define.var.count - len(self.toplevel.vars)
        type(self).var_declare_remaining = var_declare_remaining

    def choose_var_declare(self, env):
        if len(self.toplevel.vars) == 0:
            return None
        return random.choice( self.toplevel.vars )

    def choose_undefined_var(self, env):
        if len(self.undefined_vars) == 0:
            return None
        return random.choice( self.undefined_vars )

    def undefined_vars_left(self, env):
        return len(self.undefined_vars) != 0

    def declare_var(self, env):
        current_block = env.attr.current_object
        var_define = self.initialize_node( AST.ObjectVarDefine() )
        env = env.branch()
        env.attr.var_define = var_define
        var_define.name = self.get_var_name( env )
        var_define.var_path = tuple()
        self.undefined_vars.append( var_define )
        return var_define

    def get_var_name(self, env):
        name = None
        while name is None:
            letters = random.randint(2,3)
            vn = ""
            for i in range(0, letters):
                vn += random.choice(string.ascii_lowercase)
            if vn not in ["as", "to", "in"]:
                name = vn
        return name