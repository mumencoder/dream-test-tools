
from ..common import *
from ..model import *

class RandomProcs(object):
    def procs_remaining(self, env):
        if not env.attr_exists('.gen.procs_left'):
            env.attr.gen.procs_left = random.randint(0, int(len(list(self.toplevel.iter_blocks()))/2) + 2)
        return env.attr.gen.procs_left

    def create_proc(self, env, current_block):
        if type(current_block) is AST.Toplevel:
            proc_define = self.initialize_node( AST.GlobalProcDefine() )
        elif type(current_block) is AST.ObjectBlock:
            proc_define = self.initialize_node( AST.ObjectProcDefine() )
        else:
            raise Exception("bad block")
        proc_define.name = self.get_proc_name(env, current_block, proc_define)
        return proc_define

    def get_proc_name(self, env, object_block, proc_define):
        name = None
        while name is None:
            letters = random.randint(2,3)
            vn = ""
            for i in range(0, letters):
                vn += random.choice(string.ascii_lowercase)
            if vn not in ["as", "to", "in"]:
                name = vn
        return name

class SimpleProcCreator(object):
    def create_proc_params(self, env, proc_define):
        return []

    def create_proc_body(self, env, proc_define):
        stmt = self.initialize_node( AST.Stmt.Return() )
        stmt.expr = self.initialize_node( AST.Expr.Integer() )
        stmt.expr.n = random.randint(-100, 100)
        return [stmt]