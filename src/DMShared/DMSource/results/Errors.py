
from ...common import *

class Errors:
    @staticmethod
    def new_index(lines):
        index = collections.defaultdict(list)
        for line in lines:
            index[(line["file"], line["lineno"])].append( line )
        return index

    @staticmethod 
    def collect_errors(err_info, classify_fn):
        cats = set()
        for line in err_info["lines"]:
            cats.add( (line["lineno"], classify_fn( line ) ) )
        return sorted(cats, key=lambda e: e[0])

    @staticmethod
    def missing_errors(errs_l, errs_r):
        for err_l in errs_l:
            if err_l not in errs_r:
                yield err_l

    @staticmethod
    def compare_byond_opendream(byond, opendream):
        byond_index = Errors.index(byond)
        od_index = Errors.index(opendream)

        for b_idx, b_lines in byond_index.items():
            b_cats = set()
            o_cats = set()
            if b_idx in od_index:
                o_lines = od_index[b_idx]
                for line in b_lines:
                    b_cats.add( Errors.byond_category( line ) )
                for line in o_lines:
                    o_cats.add( Errors.opendream_category( line ))
                yield b_lines, b_cats, o_lines, o_cats

