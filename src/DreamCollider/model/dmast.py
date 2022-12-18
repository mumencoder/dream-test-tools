
from ..common import *
    
class AST(object):
    class Toplevel(object):
        subtree = ["leaves"]

        def __init__(self):
            self.leaves = []
            self.parent = None

    class TextNode(object):
        def __init__(self, text):
            self.text = text

    class ObjectBlock(object):
        attrs = ["name"]
        subtree = ["leaves"]
        def __init__(self):
            self.name = None
            self.leaves = []

    class GlobalVarDefine(object):
        attrs = ["name", "var_path"]
        subtree = ["expression"]
        def __init__(self):
            self.name = None            # str
            self.var_path = []          # AST.VarPath
            self.expression = None      # AST.Expr

    class ObjectVarDefine(object):
        attrs = ["name", "var_path", "is_override"]
        subtree = ["expression"]
        def __init__(self):
            self.name = None            # str
            self.var_path = []          # AST.VarPath
            self.is_override = False    # bool
            self.expression = None      # AST.Expr

    class GlobalProcDefine(object):
        attrs = ["name"]
        subtree = ["params", "body"]
        def __init__(self):
            self.name = None            # str
            self.params = []            # List[AST.ProcArgument]
            self.body = None            # List[AST.Stmt]

    class ObjectProcDefine(object):
        attrs = ["name", "is_override"]
        subtree = ["params", "body"]
        def __init__(self):
            self.name = None            # str
            self.is_override = False    # bool
            self.params = []            # List[AST.ProcArgument]
            self.body = None            # List[AST.Stmt]

    class ProcArgument(object):
        attrs = ["name", "param_type"]
        subtree = ["default", "possible_values"]
        def __init__(self):
            self.name = None            # str
            self.param_type = None      # AST.ParamPath
            self.default = None         # AST.Expr
            self.possible_values = None # ???

    class Stmt(object):
        class Expression(object):
            subtree = ["expr"]
            def __init__(self):
                self.expr = None        # AST.Expr

        class VarDefine(object):
            attrs = ["name", "var_type"]
            subtree = ["expr"]
            def __init__(self):
                self.name = None        # str
                self.var_type = None    # AST.VarPath
                self.expr = None        # AST.Expr

        class Return(object):
            subtree = ["expr"]
            def __init__(self):
                self.expr = None        # AST.Expr

        class Break(object):
            attrs = ["label"]
            def __init__(self):
                self.label = None       # str

        class Continue(object):
            attrs = ["label"]
            def __init__(self):
                self.label = None       # str

        class Goto(object):
            attrs = ["label"]
            def __init__(self):
                self.label = None       # str

        class Label(object):
            attrs = ["name"]
            subtree = ["body"]
            def __init__(self):
                self.name = None        # str
                self.body = None        # List[AST.Stmt]

        class Del(object):
            subtree = ["expr"]
            def __init__(self):
                self.expr = None        # AST.Expr

        class Set(object):
            attrs = ["attr"]
            subtree = ["expr"]
            def __init__(self):
                self.attr = None        # str
                self.expr = None        # AST.Expr

        class Spawn(object):
            subtree = ["delay", "body"]
            def __init__(self):
                self.delay = None       # AST.Expr
                self.body = None        # List[AST.Stmt]

        class If(object):
            subtree = ["condition", "truebody", "falsebody"]
            def __init__(self):
                self.condition = None   # AST.Expr
                self.truebody = None    # List[AST.Stmt]
                self.falsebody = None   # List[AST.Stmt]

        class For(object):
            subtree = ["expr1", "expr2", "expr3", "body"]
            def __init__(self):
                self.expr1 = None       # AST.Expr
                self.expr2 = None       # AST.Expr
                self.expr3 = None       # AST.Expr
                self.body = None        # List[AST.Stmt]

        class ForEnumerator(object):
            subtree = ["var_expr", "list_expr", "body"]
            def __init__(self):
                self.var_expr = None    # AST.Expr
                self.list_expr = None   # AST.Expr
                self.body = None        # List[AST.Stmt]

        class While(object):
            subtree = ["condition", "body"]
            def __init__(self):
                self.condition = None   # AST.Expr
                self.body = None        # List[AST.Stmt]

        class DoWhile(object):
            subtree = ["condition", "body"]
            def __init__(self):
                self.condition = None   # AST.Expr
                self.body = None        # List[AST.Stmt]

        class Switch(object):
            subtree = ["switch_expr", "cases"]
            def __init__(self):
                self.switch_expr = None # AST.Expr
                self.cases = None       # List[AST.Stmt.SwitchCase]

            class IfCase(object):
                subtree = ["condition", "body"]
                def __init__(self):
                    self.condition = None   # AST.Expr
                    self.body = None        # List[AST.Stmt]

            class ElseCase(object):
                subtree = ["body"]
                def __init__(self):
                    self.body = None        # List[AST.Stmt]

        class Try(object):
            subtree = ["try_body", "catch_param", "catch_body"]
            def __init__(self):
                self.try_body = None    # List[AST.Stmt]
                self.catch_param = None # AST.Expr.Catch
                self.catch_body = None  # List[AST.Stmt]

            # TODO: catch_param is procstmt in opendream
            class Catch(object):
                subtree = ["expr"]
                def __init__(self):
                    self.expr = None        # TODO: ???

        class Throw(object):
            subtree = ["expr"]
            def __init__(self):
                self.expr = None        # AST.Expr

    class Expr(object):
        class Identifier(object):
            attrs = ["name"]
            traits = ["rval", "lval", "storage", "terminal"]
            def __init__(self):
                self.name = None        # str

        class GlobalIdentifier(object):
            attrs = ["name"]
            traits = ["rval", "lval", "storage", "terminal"]
            def __init__(self):
                self.name = None        # str

        class Integer(object):
            attrs = ["n"]
            traits = ["rval", "terminal"]
            def __init__(self):
                self.n = None           # int

        class Float(object):
            attrs = ["n"]
            traits = ["rval", "terminal"]
            def __init__(self):
                self.n = None           # float

        class String(object):
            attrs = ["s"]
            traits = ["rval", "terminal"]
            def __init__(self):
                self.s = None           # str

        class FormatString(object):
            attrs = ["strings"]
            subtree = ["exprs"]
            traits = ["rval", "terminal"]
            def __init__(self):
                self.strings = None     # List[str]
                self.exprs = None       # List[AST.Expr]

        class Resource(object):
            attrs = ["s"]
            traits = ["rval", "terminal"]
            def __init__(self):
                self.s = None           # str

        class Null(object):
            traits = ["rval", "terminal"]
            def __init__(self):
                pass

        class Property(object):
            attrs = ["name"]
            traits = ["prop"]
            def __init__(self):
                self.name = None

        class Path(object):
            attrs = ["prefix", "ops", "types"]
            traits = ["rval", "path", "terminal"]
            def __init__(self):
                self.prefix = None      # str
                self.types = None       # List[str]
                self.ops = None         # List[str]

        class Call(object):
            class Param(object):
                def __init__(self):
                    self.name = None        # Union[str,None]
                    self.value = None       # AST.Expr

            class Identifier(object):
                traits = ["rval", "nonterminal"]
                def __init__(self):
                    self.name = None        # str
                    self.args = None        # List[AST.Call.Param]

            class Expr(object):
                traits = ["rval", "nonterminal"]
                def __init__(self):
                    self.expr = None        # AST.Expr
                    self.args = None        # List[AST.Call.Param]

        class Super(object):
            def __init__(self):
                pass

        class Self(object):
            traits = ["terminal", "rval", "lval"]
            def __init__(self):
                pass

    class Op(object):
        def __init__(self):
            self.exprs = []
            self.parent = None

        @staticmethod
        def add_expr(self, expr):
            self.exprs.append( expr )
            expr.parent = self

        def op_class(name, fixity, arity, prec):
            return type(name, (object,), {'fixity':fixity, 'arity':arity, 'prec':prec, '__init__':AST.Op.__init__} )

        def op(name,fixity=None, arity=None, prec=None):
            pfixity = []
            current_symbol = ""
            fixity_slot = 0
            for c in fixity:
                if c == "_":           
                    if current_symbol != "":
                        pfixity.append( current_symbol )
                        current_symbol = ""
                    pfixity.append( "_" )
                    fixity_slot += 1
                else:
                    current_symbol += c
            if current_symbol != "":
                pfixity.append( current_symbol )
            if fixity_slot != len(arity):
                raise Exception("Fixity slots does not match arity")
            op_cls = AST.Op.op_class(name, pfixity, arity, prec)
            op_cls.traits = ["nonterminal", "rval"]
            op_cls.subtree = ["exprs"]
            op_cls.add_expr = AST.Op.add_expr
            setattr(AST.Op, name, op_cls)

        def create_ops():
            h = AST.Op
            bin_expr = ["rval", "rval"]

            h.op("Paren", fixity="(_)", arity=["rval"], prec=360)
            h.op("PathUpwards", fixity="_._", arity=["path", "path"], prec=360)
            h.op("PathDownwards", fixity="_:_", arity=["path", "path"], prec=360)
            h.op("PathBranch", fixity="_/_", arity=["path", "path"], prec=360)

            h.op("Index", fixity="_[_]", arity=["storage", "rval"], prec=350)
            h.op("Deref", fixity="_._", arity=["storage", "prop"], prec=350) 
            h.op("LaxDeref", fixity="_:_", arity=["storage", "prop"], prec=350) 

            h.op("In", fixity="_in_", arity=bin_expr, prec=345)
            h.op("To", fixity="_to_", arity=bin_expr, prec=345)

            h.op("MaybeIndex", fixity="_?[_]", arity=["storage", "rval"], prec=340)
            h.op("MaybeDeref", fixity="_?._", arity=["storage", "prop"], prec=340)
            h.op("MaybeLaxDeref", fixity="_?:_", arity=["storage", "prop"], prec=340)

            h.op("Not", fixity="!_", arity=["rval"], prec=330)
            h.op("BitNot", fixity="~_", arity=["rval"], prec=330)
            h.op("Negate", fixity="-_", arity=["rval"], prec=330)
            h.op("Preinc", fixity="++_", arity=["lval"], prec=330)
            h.op("Predec", fixity="--_", arity=["lval"], prec=330)
            h.op("Postinc", fixity="_++", arity=["lval"], prec=330)
            h.op("Postdec", fixity="_--", arity=["lval"], prec=330)

            # TODO: limit on size of exponent
            h.op("Power", fixity="_**_", arity=bin_expr, prec=320)

            h.op("Multiply", fixity="_*_", arity=bin_expr, prec=310)
            h.op("Divide", fixity="_/_", arity=bin_expr, prec=310)
            h.op("Modulus", fixity="_%_", arity=bin_expr, prec=310)

            h.op("Add", fixity="_+_", arity=bin_expr, prec=300)
            h.op("Subtract", fixity="_-_", arity=bin_expr, prec=300)

            h.op("LessThan", fixity="_<_", arity=bin_expr, prec=290)
            h.op("LessEqualThan", fixity="_<=_", arity=bin_expr, prec=290)
            h.op("GreaterThan", fixity="_>_", arity=bin_expr, prec=290)
            h.op("GreaterEqualThan", fixity="_>=_", arity=bin_expr, prec=290)

            h.op("ShiftLeft", fixity="_<<_", arity=bin_expr, prec=280)
            h.op("ShiftRight", fixity="_>>_", arity=bin_expr, prec=280)

            h.op("Equals", fixity="_==_", arity=bin_expr, prec=270)
            h.op("NotEquals", fixity="_!=_", arity=bin_expr, prec=270)
            h.op("NotEquals2", fixity="_<>_", arity=bin_expr, prec=270)
            h.op("Equivalent", fixity="_~=_", arity=bin_expr, prec=270)
            h.op("NotEquivalent", fixity="_~!_", arity=bin_expr, prec=270)

            h.op("BitAnd", fixity="_&_", arity=bin_expr, prec=260)
            h.op("BitXor", fixity="_^_", arity=bin_expr, prec=250)
            h.op("BitOr", fixity="_|_", arity=bin_expr, prec=240)
            h.op("And", fixity="_&&_", arity=bin_expr, prec=230)
            h.op("Or", fixity="_||_", arity=bin_expr, prec=220)

            h.op("Ternary", fixity="_?_:_", arity=["rval", "rval", "rval"], prec=210)

            h.op("Assign", fixity="_=_", arity=["lval", "rval"], prec=200)
            h.op("AssignAdd", fixity="_+=_", arity=["lval", "rval"], prec=200)
            h.op("AssignSubtract", fixity="_-=_", arity=["lval", "rval"], prec=200)
            h.op("AssignMultiply", fixity="_*=_", arity=["lval", "rval"], prec=200)
            h.op("AssignDivide", fixity="_/=_", arity=["lval", "rval"], prec=200)
            h.op("AssignModulus", fixity="_%=_", arity=["lval", "rval"], prec=200)
            h.op("AssignBitAnd", fixity="_&=_", arity=["lval", "rval"], prec=200)
            h.op("AssignBitOr", fixity="_|=_", arity=["lval", "rval"], prec=200)
            h.op("AssignBitXor", fixity="_^=_", arity=["lval", "rval"], prec=200)
            h.op("AssignShiftLeft", fixity="_<<=_", arity=["lval", "rval"], prec=200)
            h.op("AssignShiftRight", fixity="_>>=_", arity=["lval", "rval"], prec=200)
            h.op("AssignInto", fixity="_:=_", arity=["lval", "rval"], prec=200)
            h.op("AssignAnd", fixity="_&&=_", arity=["lval", "rval"], prec=200)
            h.op("AssignOr", fixity="_||=_", arity=["lval", "rval"], prec=200)

    def print(node, s, depth=0, seen=None):
        if id(node) in seen:
            print( s.getvalue() )
            raise Exception("loop")
        seen.add( id(node) )
        t = type(node)
        if t is list:
            for e in node:
                AST.print(e, s, depth, seen=seen)
        else:
            s.write( depth*" " )
            s.write( f"{t.__name__}")
            if hasattr(node, 'attrs'):
                for attr in node.attrs:
                    s.write( f" {attr}={getattr(node, attr)}" )
            s.write( "\n" )
            if hasattr(node, 'subtree'):
                for st_attr in node.subtree:
                    s.write( (depth+1)*" ")
                    s.write( f"-{st_attr}\n" )
                    st = getattr(node, st_attr)
                    AST.print(st, s, depth+2, seen=seen)

    def to_str(node):
        s = io.StringIO()
        AST.print( node, s, seen=set() )
        return s.getvalue()

    def iter_subtree(node):
        if hasattr(node, 'subtree'):
            for st_attr in node.subtree:
                st = getattr(node, st_attr)
                if type(st) is list:
                    yield from st
                else:
                    yield from [st]

    def walk_subtree(node):
        yield node
        if hasattr(node, 'subtree'):
            for st_attr in node.subtree:
                st = getattr(node, st_attr)
                if type(st) is list:
                    for snode in st:
                        yield from AST.walk_subtree(snode)
                else:
                    yield from AST.walk_subtree(st)

    special_fns = ["initial", "issaved", "istype", "locate"]
    trait_index = collections.defaultdict(list)

    def initialize():
        AST.Op.create_ops()

        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            ty.stmt_only = False
            ty.is_op = False

        for ty in Shared.Type.iter_types(AST.Op):
            if ty is AST.Op:
                continue
            ty.is_op = True

        for ty_name in [
            "Assign", "AssignAdd", "AssignSubtract", "AssignMultiply", "AssignDivide", "AssignModulus", 
            "AssignBitAnd", "AssignBitOr", "AssignBitXor", "AssignShiftLeft", "AssignShiftRight",
            "AssignInto", "AssignAnd", "AssignOr"]:
            op = getattr(AST.Op, ty_name)
            op.stmt_only = True

        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            if hasattr(ty, 'traits'):
                for trait in ty.traits:
                    AST.trait_index[trait].append( ty )

AST.initialize()