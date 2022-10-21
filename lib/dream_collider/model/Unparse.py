
from ..common import *

from .ast import *

class Unparser(object):
    def __init__(self):
        self.s = io.StringIO()
        self.depth = 0
        self.newline = True

    def write(self, s):
        if self.newline:
            self.s.write(self.depth * " ")
        self.newline = False
        self.s.write(s)

    def begin_line(self):
        if not self.newline:
            self.s.write("\n")
            self.newline = True

    def begin_block(self):
        if not self.newline:
            self.s.write("\n")
            self.newline = True
        self.depth += 1

    def end_block(self):
        self.depth -= 1

class Unparse(object):
    class Toplevel(object):
        def unparse(self):
            upar = Unparser()
            for leaf in self.leaves:
                upar.begin_line()
                leaf.unparse(upar)
            return upar

    class ObjectBlock(object):
        def unparse(self, upar):
            upar.write( self.name )
            if len(self.leaves) == 1 and type(self.leaves[0]) is AST.ObjectBlock:
                upar.write("/")
                self.leaves[0].unparse(upar)
            else:
                upar.begin_block()
                for leaf in self.leaves:
                    upar.begin_line()
                    leaf.unparse(upar)
                upar.end_block()

    class GlobalVarDefine(object):
        def unparse(self, upar):
            upar.begin_line()
            upar.write('var/')
            for seg in self.var_path:
                upar.write( f"{seg}/" )
            upar.write( self.name )
            if self.expression is not None:
                upar.write(' = ')
                self.expression.unparse(upar)

    class ObjectVarDefine(object):
        def unparse(self, upar):
            upar.begin_line()
            upar.write('var/')
            for seg in self.var_path:
                upar.write( f"{seg}/" )
            upar.write( self.name )
            if self.expression is not None:
                upar.write(' = ')
                self.expression.unparse(upar)

    class Expr(object):
        class String(object):
            def unparse(self, upar):
                upar.write( f'"{self.s}"')
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Integer(object):
            def unparse(self, upar):
                upar.write( str(self.n) )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Float(object):
            def unparse(self, upar):
                upar.write( str(self.n) )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Identifier(object):
            def unparse(self, upar):
                upar.write( self.name )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class GlobalIdentifier(object):
            def unparse(self, upar):
                upar.write( f"global.{self.name}" )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Resource(object):
            def unparse(self, upar):
                upar.write( f"'{self.s}'" )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Null(object):
            def unparse(self, upar):
                upar.write('null')
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Super(object):
            def unparse(self, upar):
                upar.write('..')
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Self(object):
            def unparse(self, upar):
                upar.write('.')
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

    # TODO: fuzz spacing
    def unparse_expr(self, upar, parent_op=None, spacing=True):
        if parent_op and parent_op.prec >= self.prec:
            upar.write("(")

        cleaf = 0
        for e in self.fixity:
            if e == "_":
                self.exprs[cleaf].unparse_expr(upar, parent_op=self)
                cleaf += 1
            elif type(e) is str:
                if spacing:
                    upar.write(f" {e} ")
                else:
                    upar.write(f"{e}")
            else:
                raise Exception("bad fixity")

        if parent_op and parent_op.prec >= self.prec:
            upar.write(")")

    def op_unparse(self, upar):
        self.unparse_expr(upar)