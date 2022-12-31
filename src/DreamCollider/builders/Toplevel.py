
from ..common import *
from ..model import *

class Toplevel(object):
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