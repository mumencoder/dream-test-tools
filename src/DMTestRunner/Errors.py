
from .common import *

class Errors:
    @staticmethod
    def new_index(lines):
        index = collections.defaultdict(list)
        for line in lines:
            index[(line["file"], line["lineno"])].append( line )
        return index

    @staticmethod
    def byond_category(err):
        msg = err["msg"]
        if 'undefined var' in msg:
            return "UNDEF_VAR"
        if 'missing condition' in msg:
            return "MISSING_CONDITION"
        if 'illegal' in msg and '**' in msg:
            return "ILLEGAL_POWER"
        if 'expected a constant expression' in msg:
            return "EXPECTED_CONSTEXPR"
        if 'undefined type path' in msg:
            return "UNDEF_TYPEPATH"
        if "expected ':'" in msg:
            return "EXPECTED_COLON"
        if "expected as(...)" in msg:
            return "EXPECTED_AS"
        if "unexpected 'in' expression" in msg:
            return "UNEXPECTED_IN"
        if "missing left-hand argument to to" in msg:
            return "MISSING_LEFT_ARG_TO"
        if "missing left-hand argument to in" in msg:
            return "MISSING_LEFT_ARG_IN"
        if "missing left-hand argument to =" in msg:
            return "MISSING_LEFT_ARG_ASSIGN"
        if "invalid variable name: reserved word" in msg:
            return "VAR_RESERVED_WORD"
        if "missing while statement" in msg:
            return "MISSING_WHILE"
        if "previous definition" in msg:
            return "DUPLICATE_DEF"
        if "duplicate definition" in msg:
            return "DUPLICATE_DEF"
        if "attempted division by zero" in msg:
            return "ZERO_DIVIDE"
        if "definition out of place" in msg:
            return "BAD_DEFINE"
        if "var: missing comma ',' or right-paren ')'" in msg:
            return "MISSING_SOMETHING"
        return 'UNKNOWN'

    @staticmethod
    def opendream_category(err):
        msg = err["msg"]
        if 'Unknown identifier' in msg:
            return "UNDEF_VAR"
        if 'Invalid path' in msg:
            return 'UNDEF_TYPEPATH'
        if 'const operation' in msg and 'is invalid' in msg:
            return "EXPECTED_CONSTEXPR"
        if 'Unknown global' in msg:
            return "UNDEF_VAR"
        if 'Invalid initial value' in msg:
            return "INVALID_INIT"
        if 'proc' in msg and 'is already defined in global scope' in msg:
            return "DUPLICATE_GLOBAL_PROC"
        if 'Type' in msg and 'already has a proc named' in msg:
            return "DUPLICATE_OBJ_PROC"
        if 'Duplicate definition of static var' in msg:
            return "DUPLICATE_STATIC_VAR"
        if 'Duplicate definition of var' in msg:
            return "DUPLICATE_DEF"
        return 'UNKNOWN'

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
