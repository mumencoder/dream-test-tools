
from ..common import *
from ..model import *

class RandomVars(object):
    def vars_remaining(self, env):
        if not env.attr_exists('.gen.vars_left'):
            env.attr.gen.vars_left = random.randint(0, len(list(self.toplevel.iter_blocks()))*2 + 2)
        return env.attr.gen.vars_left
            
    def declare_var(self, env, current_block):
        if type(current_block) is AST.Toplevel:
            var_define = AST.GlobalVarDefine()
        elif type(current_block) is AST.ObjectBlock:
            var_define = AST.ObjectVarDefine()
        else:
            raise Exception("bad block")
        var_define.name = self.get_var_name( env, current_block, var_define )
        return var_define

    def get_var_name(self, env, object_block, var_define):
        letters = random.randint(2,3)
        vn = ""
        for i in range(0, letters):
            vn += random.choice(string.ascii_lowercase)
        return vn