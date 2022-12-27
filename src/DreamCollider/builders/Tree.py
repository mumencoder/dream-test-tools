
from ..common import *
from ..model import *

class RandomBlocks(object):
    def blocks_remaining(self, env):
        if not env.attr_exists('.gen.blocks_left'):
            env.attr.gen.blocks_left = random.randint(1, 8)
        return env.attr.gen.blocks_left

    def get_block(self, env, phase=None):
        return random.choice( list(self.toplevel.iter_blocks()) )

    def create_block(self, env, current_block):
        new_block = self.initialize_node( AST.ObjectBlock() )
        if type(current_block) is AST.Toplevel:
            new_block.name = random.choice( ['ty1', 'ty2', 'ty3'])
        else:
            new_block.name = current_block.name + random.choice( ['1', '2', '3'])
        return new_block

    def random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path
    
class Toplevel(object):
    def __init__(self):
        self.toplevel = self.initialize_node( AST.Toplevel() )

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

    def unparse(self, ngrams=None):
        upar = Unparser()

        ngram_tokens, text_tokens = itertools.tee( upar.coalesce_newlines( upar.fuzz_stream( self.toplevel.shape() ) ), 2)

        for token in upar.strip_nonprintable( text_tokens ):
            upar.write_token( token )

        self.text = upar.s.getvalue()   
        if ngrams is not None:
            self.ngram_info = ngrams.compute_info( ngram_tokens )     

    def get_model(self):
        m = {}
        m["errors"] = self.toplevel.collect_errors([])
        return m

    def print(self, out):
        AST.print( self.toplevel, out, seen=set() )