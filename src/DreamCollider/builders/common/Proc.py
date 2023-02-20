
from ...common import *
from ...model import *

class RandomProcName(object):
    def __call__(self, env):
        name = None
        while name is None:
            letters = random.randint(2,3)
            vn = ""
            for i in range(0, letters):
                vn += random.choice(string.ascii_lowercase)
            if vn not in ["as", "to", "in", "do", "if"]:
                name = vn
        return name

class RandomStdlibProcName(object):
    def __init__(self):
        pass

    def __call__(self, env):
        choices = env.attr.builder.stdlib.procs[ env.attr.current_object.resolved_path ]
        return list(choices.keys())

class ProcDeclareAction(object):
    def __init__(self, builder):
        self.config = ColliderConfig()
        self.builder = builder
        self.choose_object = None
        self.generate_proc_name = None
    
    def __call__(self, env):
        tries = 0
        current_object = None
        while current_object is None and tries < 10:
            current_object = self.choose_object(env)
            if type(current_object) is AST.ObjectBlock and ('proc' in current_object.resolved_path or 'verb' in current_object.resolved_path):
                current_object = None
            tries += 1
        if tries == 10:
            return None
        env.attr.current_object = current_object

        proc_block = env.attr.builder.initialize_node( AST.ObjectBlock.new() )
        if self.config.prob('verb_prob'):
            proc_block.path = AST.ObjectPath.new(segments=tuple(["verb"]))
        else:
            proc_block.path = AST.ObjectPath.new(segments=tuple(["proc"]))

        proc_declare = env.attr.builder.initialize_node( AST.ProcDefine.new() )
        choices = self.generate_proc_name(env)
        if len(choices) == 0:
            return None
        proc_declare.name = random.choice( choices )

        current_object.add_leaf( proc_block )
        proc_block.add_leaf( proc_declare )
        self.current_count += 1
        return True

class ProcDefineAction(object):
    def __call__(self, env):
        proc_define = env.attr.gen.initialize_node( AST.ProcDefine() )
        proc_define.name = env.attr.gen.generate_proc_name(env)
        env.attr.gen.node_info[proc_define] = {"args": max(0, random.gauss(6, 3)), "stmts": max(0, random.gauss(3, 1.5)) }
        env.attr.gen.add_tag( proc_define, "needs_random_args" )
        env.attr.gen.add_tag( proc_define, "needs_random_stmts" )
        return proc_define

class ProcParameterAction(object):
    def __init__(self, proc_tag, param_tags):
        self.proc_tag = proc_tag
        self.param_tags = param_tags

    def finished(self, env):
        procs = env.attr.find_tagged(self.proc_tag)
        return len(procs) == 0

    def __call__(self, env):
        current_proc = self.choose_proc(env)
        env.attr.current_proc = current_proc
        proc_param = self.create_proc_param(env)
        env.attr.gen.add_param( current_proc, proc_param )

class ProcStatementAction(object):
    def __init__(self, proc_tag, statement_tags):
        self.proc_tag = proc_tag
        self.statement_tags = statement_tags

    def finished(self, env):
        procs = env.attr.find_tagged(self.proc_tag)
        return len(procs) == 0

    def __call__(self, env):
        current_proc = self.choose_proc(env)
        env.attr.current_proc = current_proc
        proc_stmt = self.create_proc_stmt(env)
        env.attr.gen.add_stmt( current_proc, proc_stmt )

class RandomProcs(object):
    def config_proc(self, config):
        config.set("proc.is_verb_prob", 0.05)
        config.set("proc.arg.has_path_prob", 0.05)
        config.set("proc.arg.has_init_prob", 0.10)
        config.set("proc.arg.has_astype_prob", 0.02)

    def add_proc_paths(self, env):
        block = random.choice( self.toplevel.object_blocks )
        proc_block = self.initialize_node( AST.ObjectBlock() )
        proc_block.path = AST.ObjectPath.new( segments=['proc'] )
        block.add_leaf( proc_block )

        proc = self.initialize_node( AST.ProcDefine.new(name="print_path") )
        proc.body = []
        proc_block.add_leaf( proc )
        
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