
from ..common import *
    
class UsageError(Exception):
    pass

class AST(object):
    terminal_exprs = []
    nonterminal_exprs = []
    
    class Toplevel(object):
        subtree = ["leaves"]

        def __init__(self):
            self.leaves = []
            self.parent = None

            # local indices
            # TODO: these need to be ordered by tree position
            self.object_blocks_by_name = collections.defaultdict(list)
            self.global_vars_by_name = collections.defaultdict(list)
            self.global_procs_by_name = collections.defaultdict(list)

            # toplevel indices
            # TODO: these need to be ordered by tree position
            self.object_blocks_by_path = collections.defaultdict(list)

            self.decl_deps = collections.defaultdict(set)
            self.decl_cycles = collections.defaultdict(set)

        def get_error_count(self):
            return len(self.decl_cycles)
            
        def get_vars(self):
            return self.global_vars_by_name.values()

        def iter_blocks(self):
            yield self
            for leaf_list in self.object_blocks_by_name.values():
                for leaf in leaf_list:
                    yield leaf

        def iter_vars(self):
            for var_list in self.global_vars_by_name.values():
                for var in var_list:
                    yield var

        def iter_procs(self):
            for proc_list in self.global_procs_by_name.values():
                for proc in proc_list:
                    yield proc

        def iter_var_defines(self):
            for block in self.iter_blocks():
                for var in block.iter_vars():
                    yield var

        def iter_proc_defines(self):
            for block in self.iter_blocks():
                for proc in block.iter_procs():
                    yield proc

        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.GlobalVarDefine:
                self.global_vars_by_name[leaf.name].append( leaf )
                leaf.assign_block( self )
            elif type(leaf) is AST.GlobalProcDefine:
                self.global_procs_by_name[leaf.name].append( leaf )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self
            leaf.parent = None
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.note_object_block( leaf )
    
        def note_object_block(self, leaf):
            self.object_blocks_by_path[leaf.path].append( leaf )

        def resolve_usage(self, block, use):
            if type(block) is AST.Toplevel:
                if type(use) is AST.Expr.Identifier:
                    return self.global_vars_by_name[ use.name ][0]
                elif type(use) is AST.Expr.GlobalIdentifier:
                    return self.global_vars_by_name[ use.name ][0]
                else:
                    raise UsageError(block, use)
            elif type(block) is AST.ObjectBlock:
                if type(use) is AST.Expr.Identifier:
                    return self.object_blocks_by_path[block.path][0].object_vars_by_name[ use.name ][0]
                elif type(use) is AST.Expr.GlobalIdentifier:
                    return self.global_vars_by_name[ use.name ][0]
                else:
                    raise UsageError(block, use)
            else:
                raise UsageError(block, use)

    class TextNode(object):
        def __init__(self, text):
            self.text = text

    class ObjectBlock(object):
        attrs = ["name"]
        subtree = ["leaves"]
        def __init__(self):
            self.name = None
            self.leaves = []

            self.root = None
            self.parent = None

            # TODO: these need to be ordered by tree position
            self.object_blocks_by_name = collections.defaultdict(list)
            self.object_vars_by_name = collections.defaultdict(list)
            self.object_procs_by_name = collections.defaultdict(list)

        # TODO: compare set() performance
        def dfs_compare(nodel, noder):
            lpath = []
            cnode = nodel
            while cnode is not None:
                lpath.append(cnode)
                cnode = cnode.parent
            cnode = noder
            while cnode is not None and cnode not in lpath:
                cnode = cnode.parent
            if cnode is None:
                block = nodel.root
            else:
                block = cnode
            #TODO

        def iter_vars(self):
            for var_list in self.object_vars_by_name.values():
                for var in var_list:
                    yield var

        def iter_procs(self):
            for proc_list in self.object_procs_by_name.values():
                for proc in proc_list:
                    yield proc

        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.ObjectVarDefine:
                self.object_vars_by_name[leaf.name].append( leaf )
                leaf.assign_block(self)
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

        def get_storage_id(self):
            return f"gvd@{self.name}"

        def assign_block(self, block):
            self.block = block

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if "const" in self.var_path:
                return "const"

            return "dynamic"

        def get_usage(self, use):
            return self.block.resolve_usage(self.block, use)
            
        def validate_expression(self, expr):
            for node in AST.walk_subtree(expr):
                if node.is_usage():
                    if self.block.check_usage_cycle( self, self.get_usage(node) ) is True:
                        return False
            return expr.validate( self.block )

        def set_expression(self, expr):
            self.expression = expr
            #for node in AST.walk_subtree(expr):
            #    if node.is_usage():
            #        self.block.add_dependency( self, self.get_usage(node) )

    class ObjectVarDefine(object):
        attrs = ["name", "var_path"]
        subtree = ["expression"]
        def __init__(self):
            self.name = None            # str
            self.var_path = []          # AST.VarPath
            self.expression = None      # AST.Expr

            self.allow_override = True

        def get_storage_id(self):
            return f"ovd@{self.block.path}@{self.name}"

        def assign_block(self, block):
            self.block = block

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if "static" in self.var_path:
                return "dynamic"
            else:
                return "const"

        def get_usage(self, use):
            return self.block.root.resolve_usage(self.block, use)

        def validate_expression(self, expr):
            for node in AST.walk_subtree(expr):
                if node.is_usage():
                    if self.block.root.check_usage_cycle( self, self.get_usage(node) ) is True:
                        return False
            return expr.validate( self.block )

        def set_expression(self, expr):
            self.expression = expr
#            for node in AST.walk_subtree(expr):
#                if node.is_usage():
#                    self.block.root.add_dependency( self, self.get_usage(node) )

    class GlobalProcDefine(object):
        attrs = ["name"]
        subtree = ["params", "body"]
        def __init__(self):
            self.name = None            # str
            self.params = []            # List[AST.ProcArgument]
            self.body = None            # List[AST.Stmt]

            self.allow_override = True
            self.allow_verb = True

        def set_params(self, params):
            self.params = params

        def set_body(self, body):
            self.body = body

    class ObjectProcDefine(object):
        attrs = ["name"]
        subtree = ["params", "body"]
        def __init__(self):
            self.name = None            # str
            self.params = []            # List[AST.ProcArgument]
            self.body = None            # List[AST.Stmt]

            self.allow_override = True
            self.allow_verb = True

        def set_params(self, params):
            self.params = params

        def set_body(self, body):
            self.body = body

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
            attrs = ["strings"]
            subtree = ["exprs"]
            arity = "vararg"
            def __init__(self):
                self.strings = None     # List[str]
                self.exprs = None       # List[AST.Expr]

        class Resource(object):
            attrs = ["s"]
            terminal = True
            def __init__(self):
                self.s = None           # str

        class Null(object):
            terminal = True
            def __init__(self):
                pass

        class Path(object):
            attrs = ["prefix", "ops", "types"]
            terminal = True
            def __init__(self):
                self.prefix = None      # str
                self.types = None       # List[str]
                self.ops = None         # List[str]

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

    special_fns = ["initial", "issaved", "istype", "locate"]

    class Path(object):
        def __init__(self, segments):
            self.segments = tuple(segments)

        def parent_paths(self):
            cpath = []
            for segment in self.segments:
                cpath.append(segment)
                yield AST.Path(cpath)

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
            return AST.Path( [seg for seg in path.split("/") if seg != ""] )

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

    def initialize():
        AST.Op.create_ops()

        for ty in Shared.Type.iter_types(AST):
            if getattr(ty, 'terminal', None):
                AST.terminal_exprs.append(ty)
            if getattr(ty, 'nonterminal', None):
                AST.nonterminal_exprs.append(ty)

AST.initialize()