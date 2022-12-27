
from ..common import *

from .dmast import *

class NGram(object):
    keywords = ["var", "proc", "return"]
    symbols = ["/", "{", "}", "[", "]", "(", ")", "--", "++", 
        "~", ".", ":", "<=", ">=", "<", ">", "+", "-", "*", "%", "**", "^", "'", '"', ";", "!", "?", "?[",
        "&", "|", "||", "&&", "<<", ">>",
        "=", "==", "!=", "~!", "~=", "<>",
        "in", "to", "as"]

    begin_node_ords = {}
    end_node_ords = {}
    keyword_ords = {}
    symbol_ords = {}

    def __init__(self):
        self.calculate_ordinals()

    def ngram_to_str(self, ng):
        return ",".join(ng)
    
    def compute_info(self, tokens):
        tokens = itertools.tee( tokens, 2)
        info = {}
        info["frequency"] = self.compute_frequency( self.iter_ngram(tokens[0], 2) )
        info["token_count"] = len( list(tokens[1]) )
        return info

    def compute_frequency(self, ngs):
        frequency = collections.defaultdict(int)
        for ng in ngs:
            frequency[ self.ngram_to_str(ng) ] += 1
        return frequency

    def calculate_ordinals(self):
        i = 12
        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue    
            self.begin_node_ords[ty] = str(i)
            self.end_node_ords[ty] = str(i+1)
            i += 2
        for keyword in self.keywords:
            self.keyword_ords[keyword] = str(i)
            i += 1
        for symbol in self.symbols:
            self.symbol_ords[symbol] = str(i)
            i += 1

    def iter_ngram(self, stream, n):
        q = collections.deque()
        for token in stream:
            ctoken = self.convert_token(token)
            if ctoken is None:
                continue
            q.append( ctoken )
            if len(q) > n:
                q.popleft()
            if len(q) == n:
                yield list(q)

    def convert_token(self, token):
        if token["type"] == "Line":
            return None
        if token["type"] == "Newline":
            return "1"
        if token["type"] == "Ident":
            return "2"
        if token["type"] == "Text":
            if token["text_type"] == "indent":
                return "3"
            if token["text_type"] == "ws":
                return "4"
            if token["text_type"] == "super":
                return "5"
            if token["text_type"] == "self":
                return "6"
            if token["text_type"] == "null":
                return "7"
            if token["text_type"] == "int":
                return "8"
            if token["text_type"] == "float":
                return "9"
            if token["text_type"] == "string":
                return "10"
            if token["text_type"] == "global_id":
                return "11"
            raise Exception(token)
        if token["type"] == "Keyword":
            return self.keyword_ords[ token["text"] ]
        if token["type"] == "Symbol":
            return self.symbol_ords[ token["text"] ]
        if token["type"] == "BeginNode":
            return self.begin_node_ords[ type(token["node"]) ]
        if token["type"] == "EndNode":
            return self.end_node_ords[ type(token["node"]) ]
        raise Exception(token)