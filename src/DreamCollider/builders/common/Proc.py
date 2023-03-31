
from ...common import *
from ...model import *

from .Config import *
from .Build import *

   
### Actions
class ProcDeclareAction(Configurable):
    def __init__(self):
        self.config = ColliderConfig()
        self.choose_object = None
        self.generate_proc_name = None
    
    def __call__(self, env):
        tries = 0
        current_object = None
        while current_object is None and tries < 10:
            current_object = self.choose_object(env)
            if type(current_object) is AST.ObjectBlock and keyword_object_block(current_object.resolved_path):
                current_object = None
            tries += 1
        if tries == 10:
            return None
        env.attr.current_object = current_object

        is_override = self.config.prob('override_prob')

        if is_override:
            proc_object = None
        else:
            proc_object = env.attr.collider.builder.initialize_node( AST.ObjectBlock.new() )
            if self.config.prob('verb_prob'):
                proc_object.path = AST.ObjectPath.new(segments=tuple(["verb"]))
            else:
                proc_object.path = AST.ObjectPath.new(segments=tuple(["proc"]))

        proc_declare = env.attr.collider.builder.initialize_node( AST.ProcDefine.new() )
        choices = self.generate_proc_name(env)
        if len(choices) == 0:
            return None
        proc_declare.name = random.choice( choices )

        if proc_object is None:
            current_object.add_leaf( proc_declare )
        else:
            current_object.add_leaf( proc_object )
            proc_object.add_leaf( proc_declare )
        self.current_count += 1
        env.attr.collider.builder.undefined_procs.add( proc_declare )
        return True

class ProcParameterAction(Configurable):
    def __init__(self):
        self.config = ColliderConfig()
        self.choose_proc = None
        self.generate_proc_param = None

    def finished(self, env):
        return len(env.attr.collider.builder.undefined_procs) == 0
    
    def __call__(self, env):
        current_proc = self.choose_proc(env)
        env.attr.current_proc = current_proc
        proc_param = self.generate_proc_param(env)
        current_proc.add_param( proc_param )
        if self.config.prob('finalize_proc'):
            env.attr.collider.builder.undefined_procs.remove( current_proc )

class ProcStatementAction(Configurable):
    def __init__(self):
        self.config = ColliderConfig()
        self.choose_proc = None
        self.generate_proc_stmt = None

    def finished(self, env):
        return len(env.attr.collider.builder.undefined_procs) == 0

    def __call__(self, env):
        current_proc = self.choose_proc(env)
        env = env.branch()
        env.attr.current_proc = current_proc
        env.attr.proc_max_depth = random.randint(0,4)
        proc_stmt = self.generate_proc_stmt(env)
        current_proc.add_stmt( proc_stmt )
        if self.config.prob('finalize_proc'):
            env.attr.collider.builder.undefined_procs.remove( current_proc )

# Generators

class BasicProcName(Configurable):
    def __call__(self, env):
        return random.choice( ['a', 'b', 'c', 'd'] )
    
class RandomProcName(Configurable):
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

class RandomStdlibProcName(Configurable):
    def __init__(self):
        pass

    def __call__(self, env):
        choices = env.attr.collider.builder.stdlib.procs[ env.attr.current_object.resolved_path ]
        return list(choices.keys())

class RandomUndefinedProc(Configurable):
    def __call__(self, env):
        builder = env.attr.builder
        if len(builder.undefined_procs) == 0:
            return None
        else:
            return random.choice( list(builder.undefined_procs) )

class RandomProcParam(Configurable):
    def __call__(self, env):
        builder = env.attr.builder
        arg = builder.initialize_node( AST.ProcArgument() )
        arg.name = self.generate_string(1, 3)

        if self.config.prob('proc.arg.has_path_prob'):
            arg.path_type = AST.Expr.Path.new(segments=['static'])
        if self.config.prob('proc.arg.has_default_prob'):
            arg.default = self.generate_expression(env)
        if self.config.prob('proc.arg.has_astype_prob'):
            for i in range(0,random.randint(1,3)):
                arg.possible_values = AST.Expr.AsType()
                arg.possible_values.flags.append( self.generate_dm_valuetype(env) )
        return arg