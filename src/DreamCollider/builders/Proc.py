
from ..common import *
from ..model import *

class RandomProcs(object):
    def choose_proc_declare(self, env):
        if len(self.toplevel.procs) == 0:
            return None
        return random.choice( self.toplevel.procs )

    def proc_declare_count(self, env):
        return 2 - len(self.toplevel.procs)

    def proc_stmts_left(self, env):
        proc_stmts = 0
        for obj, info in self.proc_defines.items():
            proc_stmts += info["stmts"]
        return proc_stmts != 0

    def proc_args_left(self, env):
        proc_args = 0
        for obj, info in self.proc_defines.items():
            proc_args += info["args"]
        return proc_args != 0

    def declare_proc(self, env, current_block):
        if type(current_block) is AST.Toplevel:
            proc_define = self.initialize_node( AST.GlobalProcDefine() )
        elif type(current_block) is AST.ObjectBlock:
            proc_define = self.initialize_node( AST.ObjectProcDefine() )
            if random.random() < 0.1:
                proc_define.is_override = True
        else:
            raise Exception("bad block")
        proc_define.name = self.get_proc_name(env, current_block, proc_define)
        self.proc_defines[proc_define] = {"args": random.randint(0, 2), "stmts": random.randint(0, 4) }
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
    def create_proc_param(self, env, proc_define):
        arg = self.initialize_node( AST.ProcArgument() )
        arg.name = "arg"
        return arg

    def create_proc_stmt(self, env, proc_define):
        stmt = self.initialize_node( AST.Stmt.Return() )
        stmt.expr = self.initialize_node( AST.Expr.Integer() )
        stmt.expr.n = random.randint(-100, 100)
        return stmt