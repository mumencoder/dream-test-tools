
from ..common import *

from .dmast import *
from .Shape import *

class NGram(object):
    ignore_tokens = set( ["Line"] )

    token_types = set( ["Newline"] )
    generic_text = set( ["ws", "indent"] )
    generic_symbols = set( ["(", ")", "{", "}", ";"] )

    begin_node_ords = {}
    end_node_ords = {}

    node_ords = {}
    type_ords = {}
    text_ords = {}
    symbol_ords = {}

    @staticmethod
    def calculate_ordinals():
        i = 0

        for tt in NGram.token_types:
            NGram.type_ords[ tt ] = str(i)
            i += 1

        for tt in NGram.generic_text:
            NGram.text_ords[ tt ] = str(i)
            i += 1

        for sym in NGram.generic_symbols:
            NGram.symbol_ords[ sym ] = str(i)
            i += 1

        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue    
            NGram.begin_node_ords[ty] = str(i)
            NGram.end_node_ords[ty] = str(i+1)
            i += 2
            for token in ty.tokens_used():
                NGram.node_ords[(ty,token)] = str(i)
                i += 1

    @staticmethod
    def new_accum():
        return {"ngram_counts": collections.defaultdict(int), "token_count":0}

    @staticmethod
    def accum_count(accum, info):
        counts = accum["ngram_counts"]
        accum["token_count"] += info["token_count"]
        for k, c in info["ngram_counts"].items():
            counts[k] += c

    @staticmethod
    def score_test(pool_accum, test_accum):
        score = 0.0
        for ngram, ct in test_accum["ngram_counts"].items():
            if ngram in pool_accum["ngram_counts"]:
                base_score = pool_accum["token_count"] / pool_accum["ngram_counts"][ngram] 
                score += ct * base_score
            else:
                score += ct * pool_accum["token_count"]
        return score / test_accum["token_count"]

    @staticmethod
    def ngram_to_str(ng):
        return ",".join(ng)
    
    @staticmethod
    def compute_info(tokens):
        tokens = itertools.tee( tokens, 2)
        info = {}
        info["ngram_counts"] = NGram.compute_ngram_counts( NGram.iter_ngram(tokens[0], 2) )
        info["token_count"] = len( list(tokens[1]) )
        return info

    @staticmethod
    def compute_ngram_counts(ngs):
        counts = collections.defaultdict(int)
        for ng in ngs:
            counts[ NGram.ngram_to_str(ng) ] += 1
        return counts

    @staticmethod
    def iter_ngram(stream, n):
        si = ShapeIter(stream)
        q = collections.deque()
        for token in stream:
            si.update_state(token)
            ctoken = NGram.convert_token(si, token)
            if ctoken is None:
                continue
            q.append( ctoken )
            if len(q) > n:
                q.popleft()
            if len(q) == n:
                yield list(q)

    @staticmethod
    def convert_token(si, token):
        if token["type"] in NGram.ignore_tokens:
            return None
        if token["type"] in NGram.token_types:
            return NGram.type_ords[ token["type"] ]
        if token["type"] == "Symbol":
            key = ( type(si.current_node()), token["text"] )
            result = NGram.node_ords.get( key, None )
            if result is not None:
                return result
            elif token["text"] in NGram.generic_symbols:
                return NGram.symbol_ords[ token["text"] ]
            else:
                raise Exception("missing ordinal", token)
        if token["type"] == "Keyword":
            key = ( type(si.current_node()), token["text"] )
            return NGram.node_ords[ key ]
        if token["type"] == "Text":
            key = ( type(si.current_node()), token["subtype"] )
            result = NGram.node_ords.get( key, None )
            if result is not None:
                return result
            elif token["subtype"] in NGram.generic_text:
                return NGram.text_ords[ token["subtype"] ]
            else:
                raise Exception("missing ordinal", token)

        if token["type"] == "BeginNode":
            return NGram.begin_node_ords[ type(token["node"]) ]
        if token["type"] == "EndNode":
            return NGram.end_node_ords[ type(token["node"]) ]
        raise Exception(token)