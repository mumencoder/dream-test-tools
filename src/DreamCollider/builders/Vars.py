
from ..common import *
from ..model import *

from . import Names

class RandomVars(object):
    def vars_remaining(self, env):
        if not env.attr_exists('.gen.vars_left'):
            env.attr.gen.vars_left = random.randint(0, len(list(self.toplevel.iter_blocks()))*2 + 2)
        return env.attr.gen.vars_left
            
    def declare_var(self, env, current_block):
        if type(current_block) is AST.Toplevel:
            var_define = AST.GlobalVarDefine()
            var_define.init_ws = Unparse.GlobalVarDefine.default_ws
        elif type(current_block) is AST.ObjectBlock:
            var_define = AST.ObjectVarDefine()
            var_define.init_ws = Unparse.ObjectVarDefine.default_ws
        else:
            raise Exception("bad block")
        var_define.name = Names.randomVarName()
        return var_define