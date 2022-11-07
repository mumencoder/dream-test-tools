
from ..common import *

from .ast import *

class Unparser(object):
    def __init__(self):
        self.s = io.StringIO()
        self.depth = 0
        self.newline = True

    def write(self, s):
        if self.newline is True:
            self.s.write( self.depth*2*" ")
            self.newline = False
        self.s.write(s)

    def block_mode_newline(self, ws):
        if ws["block"] > 0:
            self.newline = True
            return "\n"
        elif ws["block"] < 0:
            return ""

    def begin_line(self, ws):
        if self.newline is False:
            self.s.write(ws)
            self.newline = True

    def end_line(self, ws):
        self.s.write(ws)

    def begin_block(self, ws):
        if type(ws) is dict:
            ws = self.convert_block_ws(ws)
        self.s.write(ws)
        self.depth += 1

    def end_block(self, ws):
        if type(ws) is dict:
            ws = self.convert_block_ws(ws)
        self.s.write(ws)
        self.depth -= 1

def Block(n):
    return {"block":n}

class Unparse(object):
    class Toplevel(object):
        def unparse(self, upar):
            for leaf in self.leaves:
                leaf.unparse(upar)
            return upar

        def default_ws(self):
            return [ ]
            
    class ObjectBlock(object):
        def unparse(self, upar):
            if self.parent is not None and len(self.parent.leaves) == 1:
                upar.write("/")
                upar.write( self.get_ws() )
                upar.write( self.name )
                self.leaves[0].unparse(upar)
            else:
                upar.begin_line( self.get_ws() )
                upar.write( self.name )
                upar.write( self.get_ws() )

            if len(self.leaves) > 1:
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for leaf in self.leaves:
                    leaf.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.write( self.get_ws() )

        def default_ws(self):
            if self.parent is not None and len(self.parent.leaves) == 1:
                ws = [ "" ]
            else:
                ws = [ "\n", "" ]
            if len(self.leaves) > 1:
                ws += [ "", Block(1), Block(-1), "" ]
            return ws

    class GlobalVarDefine(object):
        def unparse(self, upar):
            upar.begin_line( self.get_ws() )
            upar.write('var')
            upar.write( self.get_ws() )
            upar.write( "/" )
            upar.write( self.get_ws() )
            for seg in self.var_path:
                upar.write( f"{seg}" )
                upar.write( self.get_ws() )
                upar.write( f"/")
                upar.write( self.get_ws() )

            upar.write( self.name )
            if self.expression is not None:
                upar.write( self.get_ws() )
                upar.write('=')
                upar.write( self.get_ws() )
                self.expression.unparse(upar)
            upar.end_line( self.get_ws() )

        def default_ws(self):
            ws = [ "\n", "", "" ]
            for seg in self.var_path:
                ws += ["", ""]
            ws += [" ", " ", ""]
            return ws

    class ObjectVarDefine(object):
        def unparse(self, upar):
            upar.begin_line( self.get_ws() )
            upar.write('var')
            upar.write( self.get_ws() )
            upar.write( "/" )
            upar.write( self.get_ws() )
            for seg in self.var_path:
                upar.write( f"{seg}" )
                upar.write( self.get_ws() )
                upar.write( f"/")
                upar.write( self.get_ws() )

            upar.write( self.name )
            if self.expression is not None:
                upar.write( self.get_ws() )
                upar.write('=')
                upar.write( self.get_ws() )
                self.expression.unparse(upar)
            upar.end_line( self.get_ws() )
                
        def default_ws(self):
            ws = [ "\n", "", "" ]
            for seg in self.var_path:
                ws += ["", ""]
            ws += [" ", " ", ""]
            return ws

    class ObjectProcDefine(object):
        def unparse(self, upar):
            if self.parent is not None and len(self.parent.leaves) == 1:
                upar.write("/proc/")
                upar.write( self.get_ws() )
                upar.write( self.name )
            else:
                upar.begin_line( self.get_ws() )
                upar.write("proc/")
                upar.write( self.name )
                upar.write( self.get_ws() )

            upar.write( "(" )
            upar.write( self.get_ws() )
            for param in self.params:
                param.unparse(upar)
            upar.write( ")" )
            upar.write( self.get_ws() )
            upar.begin_block( self.get_ws() )
            for stmt in self.body:
                stmt.unparse(upar)
            upar.end_block( self.get_ws() )

        def default_ws(self):
            if self.parent is not None and len(self.parent.leaves) == 1:
                ws = [""]
            else:
                ws = ["\n", ""]
            ws += [ "", "", Block(1), Block(-1) ]
            return ws

    class GlobalProcDefine(object):
        def unparse(self, upar):
            upar.write( "/proc/")
            upar.write( self.name )
            upar.write( self.get_ws() )
            upar.write( "(" )
            upar.write( self.get_ws() )
            for param in self.params:
                param.unparse(upar)
            upar.write( ")" )
            upar.write( self.get_ws() )
            upar.begin_block( self.get_ws() )
            for stmt in self.body:
                stmt.unparse(upar)
            upar.end_block( self.get_ws() )

        def default_ws(self):
            return [ "", "", "", Block(1), Block(-1) ]
    class Expr(object):
        class String(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( f'"{self.s}"')
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Integer(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( str(self.n) )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Float(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( str(self.n) )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Identifier(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( self.name )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class GlobalIdentifier(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( f"global.{self.name}" )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Resource(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( f"'{self.s}'" )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Null(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write('null')
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Super(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write('..')
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Self(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write('.')
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

    class Stmt(object):
        class Return(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write('return')
                upar.write( self.get_ws() )
                self.expr.unparse_expr(upar)
                upar.write( self.get_ws() )
            def default_ws(self):
                return [ "\n", " ", "" ]

    def unparse_op(self, upar):
        def unparse(self, upar, parent_op=None):
            if parent_op and parent_op.prec >= self.prec:
                upar.write( self.get_ws() )
                upar.write("(")
                upar.write( self.get_ws() )

            cleaf = 0
            for e in self.fixity:
                if e == "_":
                    self.exprs[cleaf].unparse_op(upar, parent_op=self)
                    cleaf += 1
                elif type(e) is str:
                    if self.spacing:
                        upar.write( self.get_ws() )
                        upar.write(f"{e}")
                        upar.write( self.get_ws() )
                    else:
                        upar.write(f"{e}")
                else:
                    raise Exception("bad fixity")

            if parent_op and parent_op.prec >= self.prec:
                upar.write( self.get_ws() )
                upar.write(")")
                upar.write( self.get_ws() )
        return unparse(self, upar)

    def default_op_ws(self):
        def default_ws(self, parent_op=None):
            ws = []
            if parent_op and parent_op.prec >= self.prec:
                ws += ["", ""]
            for e in self.fixity:
                if type(e) is str and self.spacing:
                    ws += [" ", " "]
            if parent_op and parent_op.prec >= self.prec:
                ws += ["", ""]
        return default_ws(self)

    def default_terminal_ws(self):
        return ["", ""]

    def get_ws(self):
        return self.ws.popleft()

    def op_unparse(self, upar):
        self.unparse_expr(upar)

default_ws_types = {}

for ty in iter_types(AST):
    if ty in [AST.Op, AST.Expr]:
        continue
    if getattr(ty, 'terminal', None):
        default_ws_types[ty] = Unparse.default_terminal_ws
    ty.get_ws = Unparse.get_ws

for ty in iter_types(AST.Op):
    if ty is AST.Op:
        continue
    ty.stmt_only = False
    ty.unparse = Unparse.op_unparse
    default_ws_types[ty] = Unparse.default_op_ws

for ast_ty, unparse_ty in mix_types(AST, Unparse):
    if hasattr(unparse_ty, 'default_ws'):
        default_ws_types[ast_ty] = unparse_ty.default_ws

for ty_name in ["PathUpwards", "PathDownwards", "Path", "Deref", "MaybeDeref", "LaxDeref", "MaybeLaxDeref", "Index", "MaybeIndex"]:
    op = getattr(AST.Op, ty_name)
    op.spacing = False
for ty_name in [
    "Assign", "AssignAdd", "AssignSubtract", "AssignMultiply", "AssignDivide", "AssignModulus", 
    "AssignBitAnd", "AssignBitOr", "AssignBitXor", "AssignShiftLeft", "AssignShiftRight",
    "AssignInto", "AssignAnd", "AssignOr"]:
    op = getattr(AST.Op, ty_name)
    op.stmt_only = True

mix_fn(AST, Unparse, 'unparse')
mix_fn(AST, Unparse, 'unparse_expr')