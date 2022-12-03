
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
        if self.newline is False:
            self.s.write(ws)
            self.newline = True

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
            
    class TextNode(object):
        def unparse(self, upar):
            upar.write( self.text )

        def default_ws(self):
            return [ ]

    class ObjectBlock(object):
        def unparse(self, upar):
            if self.parent is None:
                upar.write( self.get_ws() )
                upar.write("/")
            if len(self.leaves) == 1 and self.leaves[0].join_path:
                upar.write( self.get_ws() )
                upar.write( self.name )
                upar.write( self.get_ws() )
                upar.write("/")
                upar.write( self.get_ws() )
                self.leaves[0].unparse( upar )
            else:
                upar.write( self.get_ws() )
                upar.write( self.name )
                upar.write( self.get_ws() )

                upar.begin_block( self.get_ws() )
                for leaf in self.leaves:
                    leaf.unparse(upar)
                upar.end_block( self.get_ws() )

        def default_ws(self):
            ws = []
            if self.parent is None:
                ws += [ "" ]
            if len(self.leaves) == 1 and self.leaves[0].join_path:
                ws += [ "", "", "" ]
            else:
                ws += [ "", "" ]
                ws += [ Block(1), Block(-1) ]
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
            ws += [" ", " ", "\n"]
            return ws

    class ObjectVarDefine(object):
        def unparse(self, upar):
            if len(self.parent.leaves) != 1:
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
            if len(self.parent.leaves) != 1:
                upar.end_line( self.get_ws() )
                
        def default_ws(self):
            ws = []
            if len(self.parent.leaves) != 1:
                ws += ['\n']
            ws += [ "", "" ]
            for seg in self.var_path:
                ws += ["", ""]
            if self.expression is not None:
                ws += [" ", " "]
            if len(self.parent.leaves) != 1:
                ws += ['\n']
            return ws

    class ObjectProcDefine(object):
        def unparse(self, upar):
            if self.parent is None:
                upar.write( self.get_ws() )
                upar.write("/")

            upar.write( self.get_ws() )
            upar.write("proc/")
            upar.write( self.get_ws() )
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
            ws = []
            if self.parent is None:
                ws += [""]
            ws += ["", "", ""]
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

    class ProcArgument(object):
        def unparse(self, upar):
            upar.write( self.get_ws() )
            if self.param_type is not None:
                self.param_type.unparse(upar)
                upar.write( self.get_ws() )
            self.write( self.name )
            upar.write( self.get_ws() )
            if self.default is not None:
                upar.write( "=" )
                upar.write( self.get_ws() )
                self.default.unparse(upar)
                upar.write( self.get_ws() )
            if self.possible_values is not None:
                upar.write( "as" )
                upar.write( self.get_ws() )
                self.possible_values.unparse(upar)
                upar.write( self.get_ws() )

        def default_ws(self):
            ws = [ "" ]
            if self.param_type is not None:
                ws += [ "" ]
            ws += [ " " ]
            if self.default is not None:
                ws += [ " ", " " ]
            if self.possible_values is not None:
                ws += [ " ", " " ]
            return ws

    class Stmt(object):
        class Expression(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                self.expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", "", "\n" ]

        class VarDefine(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "var/" )
                upar.write( self.get_ws() )
                if self.var_type is not None:
                    self.var_type.unparse(upar)
                    upar.write( self.get_ws() )
                upar.write( self.name )
                upar.write( self.get_ws() )
                if self.expr is not None:
                    upar.write("=")
                    upar.write( self.get_ws() )
                    self.expr.unparse(upar)
                    upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )

            def default_ws(self):
                ws = ["\n", "", ""]
                if self.var_type is not None:
                    ws += [ "" ]
                ws += [ " " ]
                if self.expr is not None:
                    ws += [ " ", "" ]
                ws += [ "\n" ]
                return ws

        class Return(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write('return')
                upar.write( self.get_ws() )
                self.expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", " ", "", "\n" ]

        class Break(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write('break')
                upar.write( self.get_ws() )
                upar.write( self.label )
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", " ", "", "\n" ]

        class Continue(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write('continue')
                upar.write( self.get_ws() )
                upar.write( self.label )
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", " ", "", "\n" ]

        class Goto(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write('goto')
                upar.write( self.get_ws() )
                upar.write( self.label )
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", " ", "", "\n" ]

        class Label(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( self.label )
                upar.write( self.get_ws() )
                upar.write( ":" )
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", "", "", "\n", "\n", "\n" ]

        class Del(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write('del')
                upar.write( self.get_ws() )
                self.expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return [ "\n", "", " ", "", "\n" ]

        class Set(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write("set")
                upar.write( self.get_ws() )
                upar.write( self.attr )
                upar.write( self.get_ws() )
                upar.write( "=" )
                upar.write( self.get_ws() )
                self.expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", " ", " ", " ", "", "\n"]

        class Spawn(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "spawn" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.delay.unparse(upar)
                upar.write( self.get_ws() )
                upar.write( ")" )
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", "", "", "", "", "\n", "\n", "\n"]

        class If(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "if" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.condition.unparse(upar)
                upar.write( self.get_ws() )
                upar.write( ")" )
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.truebody:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                if self.falsebody is not None:
                    upar.write( "else" )
                    upar.write( self.get_ws() )
                    upar.begin_block( self.get_ws() )
                    for stmt in self.falsebody:
                        stmt.unparse(upar)
                    upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                ws = ['\n', "", "", "", "", "", "\n", "\n"]
                if self.falsebody is not None:
                    ws += [ "", "\n", "\n" ]
                ws += [ "\n" ]
                return ws

        class For(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "for" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                # TODO: assign statements allowed here
                if self.expr1 is not None:
                    self.expr1.unparse(upar)
                    upar.write( self.get_ws() )
                if self.expr2 is not None:
                    self.expr1.unparse(upar)
                    upar.write( self.get_ws() )
                if self.expr3 is not None:
                    self.expr1.unparse(upar)
                    upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                ws = ['\n', "", "", "" ]
                if self.expr1 is not None:
                    ws += "; "
                if self.expr2 is not None:
                    ws += "; "
                if self.expr3 is not None:
                    ws += "; "
                ws += ["\n", "\n", "\n"]
                return ws

        class ForEnumerator(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "for" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.var_expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.write("in")
                upar.write( self.get_ws() )
                self.list_expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", " ", "", " ", " ", "", "\n", "\n", "\n" ]

        class While(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "while" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.condition.unparse(upar)
                upar.write( self.get_ws() )
                upar.write( ")" )
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", "", "", "", "", "\n", "\n", "\n" ]

        class DoWhile(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "do" )
                upar.begin_block( self.get_ws() )
                for stmt in self.body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.write("while")
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.condition.unparse(upar)
                upar.write( self.get_ws() )
                upar.write( ")" )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", "\n", "\n", "", "", "", "\n" ]

        class Switch(object):
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "switch" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.switch_expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.write( ")" )
                upar.begin_block( self.get_ws() )
                for case in self.cases:
                    case.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", " ", "", "", "\n", "\n", "", "\n" ]

            class IfCase(object):
                def unparse(self, upar):
                    upar.begin_line( self.get_ws() )
                    upar.write( self.get_ws() )
                    upar.write( "if" )
                    upar.write( self.get_ws() )
                    upar.write( "(" )
                    upar.write( self.get_ws() )
                    self.condition.unparse(upar)
                    upar.write( self.get_ws() )
                    upar.write( ")" )
                    upar.begin_block( self.get_ws() )
                    for stmt in self.body:
                        stmt.unparse(upar)
                    upar.end_block( self.get_ws() )
                    upar.write( self.get_ws() )
                    upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", " ", "", "", "\n", "\n", "", "\n" ]

            class ElseCase(object):
                def unparse(self, upar):
                    upar.begin_line( self.get_ws() )
                    upar.write( self.get_ws() )
                    upar.write( "else" )
                    upar.write( self.get_ws() )
                    upar.begin_block( self.get_ws() )
                    for stmt in self.body:
                        stmt.unparse(upar)
                    upar.end_block( self.get_ws() )
                    upar.write( self.get_ws() )
                    upar.end_line( self.get_ws() )
            def default_ws(self):
                return ['\n', "", "", "\n", "\n", "", "\n" ]

        class Try:
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "try" )
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.try_body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.write( "catch" )
                upar.write( self.get_ws() )
                upar.write( "(" )
                upar.write( self.get_ws() )
                self.catch_param.unparse(upar)
                upar.write( self.get_ws() )
                upar.write( ")" )
                upar.write( self.get_ws() )
                upar.begin_block( self.get_ws() )
                for stmt in self.catch_body:
                    stmt.unparse(upar)
                upar.end_block( self.get_ws() )
                upar.end_line( self.get_ws() )

            def default_ws(self):
                return ['\n', "", "", "\n", "\n", " ", "", "", "", "\n", "\n", "\n" ]

            class Catch:
                def unparse(self, upar):
                    self.expr.unparse(upar)
                def default_ws(self):
                    return []

        class Throw:
            def unparse(self, upar):
                upar.begin_line( self.get_ws() )
                upar.write( self.get_ws() )
                upar.write( "throw" )
                upar.write( self.get_ws() )
                self.expr.unparse(upar)
                upar.write( self.get_ws() )
                upar.end_line( self.get_ws() )
            def default_ws(self):
                return ["\n", "", " ", "", "\n"]

    class Expr(object):
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
                
        class String(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                upar.write( f'"{self.s}"')
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class FormatString(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                i = 0
                while i < len(self.exprs):
                    upar.write( '"' )
                    upar.write( self.strings[i] )
                    upar.write( '[' )
                    upar.write( self.get_ws() )
                    upar.write( self.exprs[i] )
                    upar.write( self.get_ws() )
                    upar.write( ']' )
                    i += 1
                upar.write( self.strings[i] )
                upar.write( '"' )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)
            def default_ws(self):
                ws = [ "" ]
                for i in range(0, len(self.exprs)):
                    ws += [ "", "" ]
                ws += [ "" ]
                return ws

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

        class Path(object):
            def unparse(self, upar):
                upar.write( self.get_ws() )
                if self.prefix is not None:
                    upar.write( self.prefix )
                i = 0
                while i < len(self.ops):
                    upar.write( self.types[i] )
                    upar.write( self.ops[i] )
                    i += 1
                upar.write( self.types[i] )
                upar.write( self.get_ws() )
            def unparse_expr(self, upar, parent_op=None):
                self.unparse(upar)

        class Call(object):
            class Identifier(object):
                def unparse(self, upar):
                    upar.write( self.get_ws() )
                    upar.write( self.name )
                    upar.write( self.get_ws() )
                    upar.write( "(" )
                    upar.write( self.get_ws() )
                    for arg in self.args:
                        arg.unparse(upar)
                    upar.write( ")" )
                    upar.write( self.get_ws() )
                def unparse_expr(self, upar, parent_op=None):
                    self.unparse(upar)
                def default_ws(self):
                    return [ "", "", "", "" ]

            class Expr(object):
                def unparse(self, upar):
                    upar.write( self.get_ws() )
                    upar.write( self.expr )
                    upar.write( self.get_ws() )
                    upar.write( "(" )
                    upar.write( self.get_ws() )
                    for arg in self.args:
                        arg.unparse(upar)
                    upar.write( self.get_ws() )
                    upar.write( ")" )
                def unparse_expr(self, upar, parent_op=None):
                    self.unparse(upar)
                def default_ws(self):
                    return [ "", "", "", "" ]

            class Param(object):
                def unparse(self, upar):
                    upar.write( self.get_ws() )
                    if self.name is not None:
                        upar.write( self.name )
                        upar.write( self.get_ws() )
                        upar.write( '=' )
                        upar.write( self.get_ws() )
                    self.value.unparse(upar)
                    upar.write( self.get_ws() )
                def unparse_expr(self, upar, parent_op=None):
                    self.unparse(upar)
                def default_ws(self):
                    ws = [ "" ]
                    if self.name is not None:
                        ws += [" ", " "]
                    ws += [ "" ]
                    return ws

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

    def unparse_op(self, upar):
        def unparse(self, upar, parent_op=None):
            if parent_op and parent_op.prec >= self.prec:
                upar.write( self.get_ws() )
                upar.write("(")
                upar.write( self.get_ws() )

            cleaf = 0
            for e in self.fixity:
                if e == "_":
                    expr = self.exprs[cleaf]
                    if hasattr(expr, 'unparse_op'):
                        expr.unparse_op(upar, parent_op=self)
                    elif hasattr(expr, 'unparse_expr'):
                        expr.unparse_expr(upar, parent_op=self)
                    else:
                        raise Exception()
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
            return ws
        return default_ws(self)

    def default_expr_ws(self):
        return ["", ""]

    def get_ws(self):
        return self.ws.popleft()

    default_ws_types = {}
        
    def initialize():
        for ty in Shared.Type.iter_types(AST):
            if ty in [AST.Op, AST.Expr]:
                continue
            ty.join_path = False
            ty.get_ws = Unparse.get_ws

        AST.ObjectBlock.join_path = True
        AST.ObjectVarDefine.join_path = True
        AST.ObjectProcDefine.join_path = True

        for ty in Shared.Type.iter_types(AST.Op):
            if ty is AST.Op:
                continue
            ty.unparse = Unparse.unparse_op
            ty.spacing = True
            Unparse.default_ws_types[ty] = Unparse.default_op_ws

        for ty in Shared.Type.iter_types(AST.Expr):
            if ty is AST.Expr:
                continue
            ty.unparse = Unparse.unparse_op
            ty.spacing = True
            Unparse.default_ws_types[ty] = Unparse.default_expr_ws

        for ast_ty, unparse_ty in Shared.Type.mix_types(AST, Unparse):
            if hasattr(unparse_ty, 'default_ws'):
                Unparse.default_ws_types[ast_ty] = unparse_ty.default_ws

        for ty_name in ["PathUpwards", "PathDownwards", "Path", "Deref", "MaybeDeref", "LaxDeref", "MaybeLaxDeref", "Index", "MaybeIndex"]:
            op = getattr(AST.Op, ty_name)
            op.spacing = False

        Shared.Type.mix_fn(AST, Unparse, 'unparse')
        Shared.Type.mix_fn(AST, Unparse, 'unparse_expr')

Unparse.initialize()