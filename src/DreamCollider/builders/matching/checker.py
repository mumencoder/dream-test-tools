
from ...common import *
from ...Tree import *

def match_hex(node):
    return node.is_hex

class ASTChecker(object):
    def __init__(self):
        self.match_index = collections.defaultdict(list)
        self.stats = collections.defaultdict(int)
        self.total_checks = 0
    
    def add_checker(self, ty, fn):
        self.match_index[ty].append( fn )

    def load_all(self):
        self.add_checker(AST.Expr.Integer, match_hex)

    def add_check_result(self, matches):
        seen_matches = set()
        for match in matches:
            if match["name"] in seen_matches:
                continue
            seen_matches.add( match["name"] )
            self.stats[ match["name"] ] += 1
        self.total_checks += 1

    def print_stat_freq(self):
        for name, match_ct in self.stats.items():
            print(name, match_ct / self.total_checks)

    def check(self, env):
        matches = []
        for node in AST.walk_subtree(env.attr.collider.builder.toplevel):
            for matcher in self.match_index[type(node)]:
                did_match = matcher(node)
                if did_match:
                    matches.append( {"name":matcher.__name__} )
        return matches
                    