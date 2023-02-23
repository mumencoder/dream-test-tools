
from ..common import *
    
class AST(object):
    class Toplevel(object):
        attrs = []
        subtree = ["leaves"]

        def __init__(self):
            self.leaves = []

    class TextNode(object):
        attrs = ["text"]
        subtree = []
        def __init__(self):
            self.text = None

    class ObjectPath(object):
        attrs = ["segments"]
        subtree = []
        def __init__(self):
            self.segments = []              # List[str] 

    class ObjectBlock(object):
        attrs = []
        subtree = ["path", "leaves"]
        def __init__(self):
            self.path = None                # AST.ObjectPath  
            self.leaves = []                # List[AST.ObjectBlock|AST.ObjectVarDefine|AST.ProcDefine]

    class ObjectVarDefine(object):
        attrs = ["is_override"]
        subtree = ["name", "expression"]
        def __init__(self):
            self.name = None               # str  
            self.expression = None         # AST.Expr
    class ProcDefine(object):
        attrs = []
        subtree = ["name", "params", "body"]
        def __init__(self):
            self.name = None              # str  
            self.params = []              # List[AST.ProcArgument]
            self.body = []                # List[AST.Stmt]

    class ProcArgument(object):
        attrs = ["name"]
        subtree = ["path_type", "default", "possible_values"]
        def __init__(self):
            self.name = None                    # str
            self.path_type = None               # AST.Path
            self.default = None                 # AST.Expr
            self.possible_values = None         # AST.AsType

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
            traits = ["rval", "lval", "storage", "terminal", "callable"]
            def __init__(self):
                self.name = None        # str

        class GlobalIdentifier(object):
            attrs = ["name"]
            traits = ["rval", "lval", "storage", "terminal", "callable"]
            def __init__(self):
                self.name = None        # str

        class Integer(object):
            attrs = ["n"]
            traits = ["rval", "terminal", "numeric"]
            def __init__(self):
                self.n = None           # int

        class Float(object):
            attrs = ["n"]
            traits = ["rval", "terminal", "numeric"]
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
            traits = ["rval", "nonterminal"]
            def __init__(self):
                self.strings = []      # List[str]
                self.exprs = []        # List[AST.Expr]

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
            attrs = ["segments"]
            traits = ["rval", "path", "terminal", "callable"]
            def __init__(self):
                self.segments = None    # List[str]

        class Call(object):
            subtree = ["expr", "args"]
            traits = ["rval", "nonterminal"]
            def __init__(self):
                self.expr = None        # AST.Expr
                self.args = []          # List[AST.Call.Param]

            class Param(object):
                attrs = ["name"]
                subtree = ["value"]
                def __init__(self):
                    self.name = None        # Union[str,None]
                    self.value = None       # AST.Expr

        class AsType(object):
            attrs = ["flags"]
            traits = ["astype"]
            def __init__(self):
                self.flags = []             # List[str]

        class Super(object):
            traits = ["terminal", "callable"]
            def __init__(self):
                pass

        class Self(object):
            traits = ["terminal", "rval", "lval"]
            def __init__(self):
                pass

        class Input(object):
            subtree = ["args", "in_list"]
            attrs = ["as_type"]
            traits = ["rval", "nonterminal"]
            def __init__(self):
                self.args = []              # List[AST.Call.Param]
                self.as_type = None         # str
                self.in_list = None         # AST.Expr

        class ModifiedType(object):
            subtree = ["mods", "path"]
            traits = ["rval", "nonterminal"]
            def __init__(self):
                self.path = None            # AST.Expr.Path
                self.mods = []              # List[AST.Expr.ModifiedType.Mod]
            
            class Mod(object):
                attrs = ["var"]
                subtree = ["val"]
                def __init__(self):
                    self.var = None         # str
                    self.val = None         # AST.Expr
                    
        class Pick(object):
            attrs = ["syntax_mode"]
            subtree = ["options"]
            traits = ["rval", "nonterminal"]
            def __init__(self):
                self.syntax_mode = None     # str
                self.options = []           # List[AST.Expr.Pick.Entry]

            class Entry(object):
                subtree = ["p", "val"]
                def __init__(self):
                    self.p = None           # AST.Expr
                    self.val = None         # AST.Expr

        class New(object):
            subtree = ["args"]
            traits = ["rval", "nonterminal"]
            def __init__(self):
                self.args = []            # List[AST.Call.Param]

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
            op_cls.attrs = []
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
        if seen is None:
            seen = set()
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

    def new_protofn(ty):
        def new(**attrs):
            node = ty()
            for k, v in attrs.items():
                if k not in ty.attrs and k not in ty.subtree:
                    raise Exception("invalid leaf")
                setattr(node, k, v)
            return node
        return new

    def marshall(node):
        if node is None:
            return node
        ty = type(node)
        fields = { }
        for attr in ty.attrs:
            fields[attr] = getattr(node, attr)
        for attr in ty.subtree:
            v = getattr(node, attr)
            if type(v) is list:
                fields[attr] = [AST.marshall(n) for n in v]
            else:
                fields[attr] = AST.marshall( v ) 
        fields["_subtree"] = AST.marshall_ty2str[ty]
        if not hasattr(node, 'marshall_id'):
            fields["_id"] = id(node)
        else:
            fields["_id"] = node.marshall_id

        return fields

    def unmarshall(data):
        if data is None:
            return data
        if "_subtree" not in data:
            raise Exception("expected _subtree", data.keys())
        ty = AST.marshall_str2ty[ data["_subtree"] ]
        node = ty()
        for attr in ty.attrs:
            setattr(node, attr, data[attr])
        for attr in ty.subtree:
            if type(data[attr]) is list:
                setattr(node, attr, [AST.unmarshall(d) for d in data[attr]])
            else:
                setattr(node, attr, AST.unmarshall(data[attr]))
        node.marshall_id = data["_id"]
        return node

    def count_nodes_by_type(node, idx=None):
        if idx is None:
            idx = collections.defaultdict(int)
        for subnode in AST.walk_subtree(node):
            idx[ type(subnode) ] += 1
        return idx

    trait_index = collections.defaultdict(list)

    def initialize():
        AST.Op.create_ops()

        AST.marshall_names = set()
        AST.marshall_ty2str = {}
        AST.marshall_str2ty = {}
        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr, AST.Stmt]:
                continue
            if ty.__name__ in AST.marshall_names:
                raise Exception("node name clash", ty)
            AST.marshall_names.add( ty.__name__ )
            AST.marshall_ty2str[ ty ] = ty.__name__
            AST.marshall_str2ty[ ty.__name__ ] = ty 
            if not hasattr(ty, 'subtree'):
                ty.subtree = []
            if not hasattr(ty, 'traits'):
                ty.traits = []
            if not hasattr(ty, 'attrs'):
                ty.attrs = []

        for ty in Shared.Type.iter_types(AST.Stmt):
            if ty in [AST, AST.Op, AST.Expr, AST.Stmt]:
                continue
            ty.traits.append( "stmt" )

        for ty in Shared.Type.iter_types(AST.Expr):
            if ty in [AST, AST.Op, AST.Expr, AST.Stmt]:
                continue
            ty.traits.append( "expr" )

        for ty in Shared.Type.iter_types(AST.Op):
            if ty in [AST, AST.Op, AST.Expr, AST.Stmt]:
                continue
            ty.traits.append( "expr" )
            ty.traits.append( "op" )

        for ty_name in [
            "Assign", "AssignAdd", "AssignSubtract", "AssignMultiply", "AssignDivide", "AssignModulus", 
            "AssignBitAnd", "AssignBitOr", "AssignBitXor", "AssignShiftLeft", "AssignShiftRight",
            "AssignInto", "AssignAnd", "AssignOr"]:
            op = getattr(AST.Op, ty_name)
            op.traits.append( "stmt" )
            op.traits.remove( "expr" )

        for ty_name in ["Deref", "LaxDeref", "MaybeDeref", "MaybeLaxDeref"]:
            op = getattr(AST.Op, ty_name)
            op.traits.append( "callable" )
            op.traits.append( "deref" )
            op.traits.append( "lval" )

        for ty_name in ["Index", "MaybeIndex"]:
            op = getattr(AST.Op, ty_name)
            op.traits.append( "callable" )
            op.traits.append( "index" )
            op.traits.append( "lval" )

        AST.Op.ShiftLeft.traits.append( "stmt" )
        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            ty.new = AST.new_protofn(ty)
            if hasattr(ty, 'traits'):
                for trait in ty.traits:
                    AST.trait_index[trait].append( ty )

        def safe_setattr(self, attr, value):
            if attr == "errors":
                pass
            # Semantics
            elif type(self) is AST.Toplevel and attr in [
                "tree", "object_blocks", 
                "stdlib", "stdlib_object_blocks",
                "object_blocks_by_path", "global_vars_by_name", "global_procs_by_name", "vars", "procs",  "decl_deps", "decl_cycles"]:
                pass
            elif type(self) is AST.ObjectBlock and attr in [
                "resolved_path", "block", "root", "object_vars_by_name", "object_procs_by_name", "path"]:
                pass
            elif type(self) is AST.ObjectVarDefine and attr in ["root", "block", "is_global", "is_override", "var_path"]:
                pass
            elif type(self) is AST.ProcDefine and attr in ["root", "block", "is_global", "is_override"]:
                pass
            elif attr in ["parent"]:
                pass
            # Marshall relevant fields
            elif attr in ["marshall_id"]:
                pass
            elif attr in type(self).attrs or attr in type(self).subtree:
                pass
            else:
                raise Exception(f"attempt to set {attr} in {self}")
            return object.__setattr__(self, attr, value)

        for ty in Shared.Type.iter_types(AST):
            ty.set_attrs = set()
            ty.__setattr__ = safe_setattr

AST.initialize()