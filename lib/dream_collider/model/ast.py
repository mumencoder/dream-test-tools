
from ..common import *

class AST(object):
    terminal_exprs = []
    nonterminal_exprs = []

    class Toplevel(object):
        subtree = ["leaves"]

        def __init__(self):
            self.leaves = []
            self.parent = None

            # local indices
            self.object_blocks_by_name = collections.defaultdict(list)
            self.global_vars_by_name = collections.defaultdict(list)
            self.global_procs_by_name = collections.defaultdict(list)

            # toplevel indices
            self.object_blocks_by_path = collections.defaultdict(list)

        def get_vars(self):
            return self.global_vars_by_name.values()

        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.GlobalVarDefine:
                self.global_vars_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.GlobalProcDefine:
                self.global_procs_by_name[leaf.name].append( leaf )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.note_object_block( leaf )
    
        def note_object_block(self, leaf):
            self.object_blocks_by_path[leaf.path].append( leaf )

    class ObjectBlock(object):
        attrs = ["name"]
        subtree = ["leaves"]
        def __init__(self):
            self.name = None
            self.leaves = []

            self.parent = None

            self.object_blocks_by_name = collections.defaultdict(list)
            self.object_vars_by_name = collections.defaultdict(list)
            self.object_procs_by_name = collections.defaultdict(list)

        def get_vars(self):
            return self.object_vars_by_name.values()

        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.ObjectVarDefine:
                self.object_vars_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.ObjectProcDefine:
                self.object_procs_by_name[leaf.name].append( leaf )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self.root
            leaf.parent = self
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.root.note_object_block( leaf )

        def compute_path(self):
            path = []
            cnode = self
            while cnode is not None:
                path.append(cnode.name)
                cnode = cnode.parent
            self.path = AST.Path( list(reversed(path)) )

        # TODO: support parent_type assignment
        def parent_chain(self, include_self=True, include_root=True):
            if include_self:
                cnode = self
            else:
                cnode = self.parent
            while cnode is not None:
                yield cnode
                cnode = cnode.parent
            if include_root:
                yield self.root

    class GlobalVarDefine(object):
        attrs = ["name", "var_path"]
        subtree = ["expression"]
        def __init__(self):
            self.name = None            # str
            self.var_path = []          # AST.VarPath
            self.expression = None      # AST.Expr

            self.allow_override = True

    class ObjectVarDefine(object):
        attrs = ["name", "var_path"]
        subtree = ["expression"]
        def __init__(self):
            self.name = None            # str
            self.var_path = []          # AST.VarPath
            self.expression = None      # AST.Expr

            self.allow_override = True

    #AST.Type("object_multivar_define", node_type=["object_define"], 
    #    attrs=AST.Attrs(defines=AST.List("object_var_define")) )

    class GlobalProcDefine(object):
        attrs = ["name"]
        subtree = ["params", "body"]
        def __init__(self):
            self.name = None            # str
            self.params = []            # List[AST.ProcArgument]
            self.body = None            # List[AST.Stmt]

            self.allow_override = True
            self.allow_verb = True

    #AST.Type("proc_multivar_define", node_type=["proc_stmt"],
    #    attrs=AST.Attrs(defines=AST.List("proc_var_define")))

    class ObjectProcDefine(object):
        attrs = ["name"]
        subtree = ["params", "body"]
        def __init__(self):
            self.name = None            # str
            self.params = []            # List[AST.ProcArgument]
            self.body = None            # List[AST.Stmt]

            self.allow_override = True
            self.allow_verb = True

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
            subtree = ["var_expr", "list_expr"]
            def __init__(self):
                self.var_expr = None    # AST.Expr
                self.list_expr = None   # AST.Expr

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

            class Case(object):
                subtree = ["start", "end"]
                def __init__(self):
                    self.start = None       # AST.Expr
                    self.end = None         # AST.Expr

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

        # TODO: browse
        # TODO: browseresource
        # TODO: outputcontrol

    class Expr(object):
        class Identifier(object):
            attrs = ["name"]
            terminal = True
            def __init__(self):
                self.name = None        # str

        class GlobalIdentifier(object):
            attrs = ["name"]
            terminal = True
            def __init__(self):
                self.name = None        # str

        class Integer(object):
            attrs = ["n"]
            terminal = True
            def __init__(self):
                self.n = None           # int

        class Float(object):
            attrs = ["n"]
            terminal = True
            def __init__(self):
                self.n = None           # float

        class String(object):
            attrs = ["s"]
            terminal = True
            def __init__(self):
                self.s = None           # str

        class FormatString(object):
            attrs = ["s"]
            subtree = ["exprs"]
            arity = "vararg"
            def __init__(self):
                self.s = None           # str
                self.exprs = None       # List[AST.Expr]

        class Resource(object):
            attrs = ["s"]
            def __init__(self):
                self.s = None           # str

        class Null(object):
            terminal = True
            def __init__(self):
                pass

        class List(object):
            arity = "vararg"
            def __init__(self):
                self.params = None      # List[AST.ListParam]

            class Param(object):
                arity = "vararg"
                def __init__(self):
                    self.name = None        # TODO: ???
                    self.value = None       # AST.Expr

        class Call(object):
            class Param(object):
                arity = "vararg"
                def __init__(self):
                    self.name = None        # Union[str,None]
                    self.value = None       # AST.Expr

            class Identifier(object):
                arity = "vararg"
                def __init__(self):
                    self.name = None        # str
                    self.args = None        # List[AST.Call.Param]

            class Expr(object):
                arity = "vararg"
                def __init__(self):
                    self.expr = None        # AST.Expr
                    self.args = None        # List[AST.Call.Param]

        class Super(object):
            def __init__(self):
                pass

        class Self(object):
            terminal = True
            def __init__(self):
                pass

        # TODO: DMASTAddText
        # TODO: DMASTProb
        # TODO: DMASTNewList
        # TODO: DMASTInput
        # TODO: DMASTPick
        # TODO: DMASTVarDeclExpression
        # TODO: DMASTNewPath
        # TODO: DMASTNewIdentifier
        # TODO: DMASTNewDereference
        # TODO: DMASTNewListIndex
        # TODO: DMASTNewInferred
        # TODO: DMASTExpressionInRange

    class Op(object):
        def __init__(self):
            self.exprs = []

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
            op_cls.nonterminal = True
            op_cls.subtree = ["exprs"]
            setattr(AST.Op, name, op_cls)

        def create_ops():
            h = AST.Op
            bin_expr = ["rval", "rval"]

            h.op("Paren", fixity="(_)", arity=["rval"], prec=360)
            h.op("PathUpwards", fixity="_._", arity=["path", "path"], prec=360)
            h.op("PathDownwards", fixity="_:_", arity=["path", "path"], prec=360)
            h.op("Path", fixity="_/_", arity=["path", "path"], prec=360)

            h.op("Index", fixity="_[_]", arity=["storage", "rval"], prec=350)
            h.op("Deref", fixity="_._", arity=["storage", "prop"], prec=350) 
            h.op("LaxDeref", fixity="_:_", arity=["storage", "prop"], prec=350) 

            h.op("In", fixity="_in_", arity=bin_expr, prec=345)
            h.op("To", fixity="_to_", arity=bin_expr, prec=345)

            h.op("MaybeIndex", fixity="_?[_]", arity=["storage", "rval"], prec=340)
            h.op("MaybeDeref", fixity="_?._", arity=["storage", "prop"], prec=340)
            h.op("MaybeLaxDeref", fixity="_?:_", arity=["storage", "prop"], prec=340)

            h.op("Not", fixity="!_", arity=["rval"], prec=330)
            h.op("Bitnot", fixity="~_", arity=["rval"], prec=330)
            h.op("Negate", fixity="-_", arity=["rval"], prec=330)
            h.op("Preinc", fixity="++_", arity=["lval"], prec=330)
            h.op("Predec", fixity="--_", arity=["lval"], prec=330)
            h.op("Postinc", fixity="_++", arity=["lval"], prec=330)
            h.op("Postdec", fixity="_--", arity=["lval"], prec=330)

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

        def create_stmts():
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

    special_fns = ["initial", "issaved", "istype", "locate"]

    class Path(object):
        def __init__(self, segments):
            self.segments = tuple(segments)

        def parent_paths(self):
            cpath = []
            for segment in self.segments:
                cpath.append(segment)
                yield Path(cpath)

        def parent_type(trunk_path, leaf_path):
            old_trunk = leaf.obj_trunk
            if old_trunk is not None:
                old_trunk.remove_child( leaf )
            leaf.new_parent( trunk )

        def contains(self, path):
            for i, segment in enumerate(path.segments):
                if i >= len(self.segments):
                    return False
                if segment != self.segments[i]:
                    return False
            return True

        def __str__(self):
            return str(self.segments)

        def __eq__(self, o):
            return self.segments == o.segments

        def __hash__(self):
            return hash(self.segments)

        def from_string(path):
            return Path( [seg for seg in path.split("/") if seg != ""] )

    class ObjectVarDecl(object):
        def initialization_mode(self, config):
            dmobj = config['model'].ensure_object(self.path)

            for o in dmobj.parent_chain(include_self=False):
                if self.name in o.scope.vars:
                    override_decl = o.scope.vars[self.name]
                    return override_decl.initialization_mode(config)

            if "const" in self.flags:
                return "const"

            if str(self.path) == "/":
                return "dynamic"
            elif "static" in self.flags:
                return "dynamic"
            else:
                return "const"

    def compute_overrides(self):
        known_vars = {}
        known_procs = {}
        for decl in self.vars:
            decl.is_override = False
        for decl in self.procs:
            if decl.name in known_procs:
                decl.is_override = True
            else:
                decl.is_override = False 
            known_procs[decl.name] = decl

        for path, dmobj in self.objects_by_path.items():
            if dmobj.obj_trunk is None:
                dmobj.compute_overrides()

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

AST.Op.create_ops()

for ty in iter_types(AST):
    if getattr(ty, 'terminal', None):
        AST.terminal_exprs.append(ty)
    if getattr(ty, 'nonterminal', None):
        AST.nonterminal_exprs.append(ty)

def mix():
    from .Unparse import Unparse
    mix_fn(AST, Unparse, 'unparse')
    mix_fn(AST, Unparse, 'unparse_expr')

mix()