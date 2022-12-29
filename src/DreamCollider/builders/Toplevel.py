
from ..common import *
from ..model import *

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