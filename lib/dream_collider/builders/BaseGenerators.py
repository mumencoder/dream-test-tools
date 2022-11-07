
from ..common import *
from ..model import *

import Shared
from . import Names

class RandomBlocks(object):
    def blocks_remaining(self, env):
        if not env.attr_exists('.gen.blocks_left'):
            env.attr.gen.blocks_left = random.randint(1, 8)
        return env.attr.gen.blocks_left

    def get_block(self, env, phase=None):
        return random.choice( list(self.toplevel.iter_blocks()) )

    def create_block(self, env, current_block):
        new_block = AST.ObjectBlock()
        if type(current_block) is AST.Toplevel:
            new_block.name = random.choice( ['ty1', 'ty2', 'ty3'])
        else:
            new_block.name = current_block.name + random.choice( ['1', '2', '3'])
        new_block.init_ws = Unparse.ObjectBlock.default_ws
        return new_block

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

class RandomProcs(object):
    def procs_remaining(self, env):
        if not env.attr_exists('.gen.procs_left'):
            env.attr.gen.procs_left = random.randint(0, int(len(list(self.toplevel.iter_blocks()))/2) + 2)
        return env.attr.gen.procs_left

    def create_proc(self, env, current_block):
        if type(current_block) is AST.Toplevel:
            proc_define = AST.GlobalProcDefine()
        elif type(current_block) is AST.ObjectBlock:
            proc_define = AST.ObjectProcDefine()
        else:
            raise Exception("bad block")
        proc_define.name = Names.randomProcName()
        return proc_define

class SimpleVarExprCreator(object):
    def create_var_expr(self, env, var_define):
        expr = AST.Expr.Integer()
        expr.n = random.randint(-100,100)
        return expr

class SimpleProcCreator(object):
    def create_proc_params(self, env, proc_define):
        return []

    def create_proc_body(self, env, proc_define):
        stmt = AST.Stmt.Return()
        stmt.expr = AST.Expr.Integer()
        stmt.expr.n = random.randint(-100, 100)
        return [stmt]

class BaseGenerator(object):
    def __init__(self):
        self.toplevel = AST.Toplevel()

    def generate(self, env):
        while self.blocks_remaining(env):
            current_block = self.get_block(env, phase="block")
            gen_block = self.create_block(env, current_block)
            current_block.add_leaf( gen_block )
            env.attr.gen.blocks_left -= 1

        while self.vars_remaining(env):
            current_block = self.get_block(env, phase="var")
            var_define = self.declare_var(env, current_block)
            current_block.add_leaf( var_define )
            env.attr.gen.vars_left -= 1

        while self.procs_remaining(env):
            current_block = self.get_block(env, phase="proc")
            proc_define = self.create_proc(env, current_block)
            current_block.add_leaf( proc_define )
            env.attr.gen.procs_left -= 1

        for var_define in self.toplevel.iter_var_defines():
            expr = self.create_var_expr(env, var_define)
            var_define.set_expression( expr )

        for proc_define in self.toplevel.iter_proc_defines():
            proc_params = self.create_proc_params(env, proc_define)
            proc_body = self.create_proc_body(env, proc_define)
            proc_define.set_params( proc_params )
            proc_define.set_body( proc_body )