
from ..common import *
from ..model import *

class RandomVars(object):
    def choose_var_declare(self, env):
        if len(self.toplevel.vars) == 0:
            return None
        return random.choice( self.toplevel.vars )

    def choose_undefined_var(self, env):
        if len(self.var_defines) == 0:
            return None
        return random.choice( self.var_defines )

    def var_declare_count(self, env):
        return 2 - len(self.toplevel.vars)

    def undefined_vars_left(self, env):
        return len(self.var_defines) != 0

    def declare_var(self, env, current_block):
        if type(current_block) is AST.Toplevel:
            var_define = self.initialize_node( AST.GlobalVarDefine() )
        elif type(current_block) is AST.ObjectBlock:
            var_define = self.initialize_node( AST.ObjectVarDefine() )
            if random.random() < 0.1:
                var_define.is_override = True
        else:
            raise Exception("bad block")
        var_define.name = self.get_var_name( env, current_block, var_define )
        self.var_defines.append( var_define )
        return var_define

    def get_var_name(self, env, object_block, var_define):
        name = None
        while name is None:
            letters = random.randint(2,3)
            vn = ""
            for i in range(0, letters):
                vn += random.choice(string.ascii_lowercase)
            if vn not in ["as", "to", "in"]:
                name = vn
        return name