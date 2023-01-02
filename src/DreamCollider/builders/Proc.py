
from ..common import *
from ..model import *

class RandomProcs(object):
    def choose_proc_declare(self, env):
        if len(self.toplevel.procs) == 0:
            return None
        return random.choice( self.toplevel.procs )

    def proc_stmts_left(self, env):
        proc_stmts = 0
        for obj, info in self.proc_defines.items():
            proc_stmts += info["stmts"]
        return proc_stmts > 0

    def proc_args_left(self, env):
        proc_args = 0
        for obj, info in self.proc_defines.items():
            proc_args += info["args"]
        return proc_args > 0

    def declare_proc(self, env):
        current_block = env.attr.current_object
        if type(current_block) is AST.Toplevel:
            proc_define = self.initialize_node( AST.GlobalProcDefine() )
        elif type(current_block) is AST.ObjectBlock:
            proc_define = self.initialize_node( AST.ObjectProcDefine() )
        else:
            raise Exception("bad block")
        env = env.branch()
        env.attr.proc_define = proc_define
        proc_define.name = self.get_proc_name(env)
        self.proc_defines[proc_define] = {"args": self.determine_proc_arg_count(env), "stmts": self.determine_proc_stmt_count(env) }
        return proc_define

    def get_proc_name(self, env):
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
    def create_proc_param(self, env):
        arg = self.initialize_node( AST.ProcArgument() )
        arg.name = self.randomString(1, 3)

        if random.random() < self.config.attr.define.proc.arg.has_path_prob:
            arg.path_type = self.random_path()
        if random.random() < self.config.attr.define.proc.arg.has_default_prob:
            arg.default = self.expression(env, depth=3, arity="rval")
        if random.random() < self.config.attr.define.proc.arg.has_astype_prob:
            for i in range(0,random.randint(1,3)):
                arg.possible_values = AST.Expr.AsType()
                arg.possible_values.flags.append( self.randomDMValueType() )
        return arg