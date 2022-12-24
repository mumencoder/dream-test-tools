
from ..common import *

from .dmast import *

def _Line():
    return {"type":"Line"}
def _BeginNode(node):
    return {"type":"BeginNode", "node":node}
def _EndNode(node):
    return {"type":"EndNode", "node":node}

def _Symbol(text):
    return {"type":"Symbol", "text":text}
def _Ident(text, type=None):
    return {"type":"Ident", "text":text, "id_type":type}
def _Keyword(text):
    return {"type":"Keyword", "text":text}
def _Exact(text):
    return {"type":"Exact", "text":text}
def _BeginParen():
    return {"type":"BeginParen"}
def _EndParen():
    return {"type":"EndParen"}
def _Newline():
    return {"type":"Newline"}
def _Whitespace(n=0):
    return {"type":"Whitespace", "n":n}

def _BeginBlock():
    return {"type":"BeginBlock"}
def _EndBlock():
    return {"type":"EndBlock"}
def _BeginLine():
    return {"type":"BeginLine"}
def _EndLine():
    return {"type":"EndLine"}

def _Fuzz():
    return {"type":"Fuzz"}

class Unparser(object):
    def __init__(self):
        self.s = io.StringIO()
        self.current_line = 1

        self.block_mode = [ {"type":"toplevel", 'indent':''} ]
        self.node_stack = []
        self.newline = True

    def raw_write(self, s):
        self.current_line += s.count('\n')
        if len(s) > 0:
            if s[-1] == '\n':
                self.newline = True
            else:
                self.newline = False
        self.s.write(s)

    def process_token(self, token):
        if token["type"] == "Line":
            node = self.node_stack[-1]
            if not hasattr(node, 'lineno'):
                node.lineno = self.current_line
        elif token["type"] == "BeginNode":
            self.node_stack.append( token["node"] )
        elif token["type"] == "EndNode":
            self.node_stack.pop()
        elif token["type"] == "Exact":
            self.raw_write( token["text"] )
        elif token["type"] == "Symbol":
            self.raw_write( token["text"] )
        elif token["type"] == "BeginParen":
            self.raw_write( '(' )
        elif token["type"] == "EndParen":
            self.raw_write( ')' )
        elif token["type"] == "Ident":
            self.raw_write( token["text"] )
        elif token["type"] == "Keyword":
            self.raw_write( token["text"] )
        elif token["type"] == "Fuzz":
            pass
        elif token["type"] == "BeginBlock":
            # TODO: check for single leafs in node
            if self.block_mode[-1]["type"] == "oneline":
                self.block_mode.append( {"type":"oneline"} )
            else:
                a = random.random()
                if a < 0.33:
                    self.block_mode.append( {"type":"oneline"} )
                elif a < 0.66:
                    self.block_mode.append( {"type":"indent", "indent": self.inc_indent()} )
                else:
                    self.block_mode.append( {"type":"nice_bracket", "indent": self.inc_indent()})
            self.begin_block()
        elif token["type"] == "EndBlock":
            self.end_block()
            self.block_mode.pop()
        elif token["type"] == "BeginLine":
            self.begin_line()
        elif token["type"] == "EndLine":
            self.end_line()
        elif token["type"] == "Newline":
            self.raw_write('\n')
        elif token["type"] == "Whitespace":
            if token["n"] == 0:
                a = random.random()
                if a < 0.5:
                    self.raw_write(" ")
            if token["n"] == 1:
                a = random.random()
                if a < 0.95:
                    self.raw_write(" ")
        else:
            raise Exception("unknown token", token)

    def begin_block(self):
        if self.block_mode[-1]["type"] == "oneline":
            self.process_token( _Symbol('{') )
            self.process_token( _Whitespace(1) )
        elif self.block_mode[-1]["type"] == "indent":
            self.process_token( _Newline() )
            self.write_indent( self.block_mode[-1] )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            self.process_token( _Symbol('{') )
            self.process_token( _Fuzz() )
            self.process_token( _Newline() )
            self.write_indent( self.block_mode[-1] )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def end_block(self):
        if self.block_mode[-1]["type"] == "oneline":
            self.process_token( _Symbol('}') )
            self.process_token( _Whitespace(1) )
        elif self.block_mode[-1]["type"] == "indent":
            pass
        elif self.block_mode[-1]["type"] == "nice_bracket":
            self.process_token( _Newline() )
            self.write_indent( self.block_mode[-2] )
            self.process_token( _Symbol('}') )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def begin_line(self):
        if self.block_mode[-1]["type"] == "oneline":
            pass
        elif self.block_mode[-1]["type"] == "toplevel":
            pass
        elif self.block_mode[-1]["type"] == "indent":
            if not self.newline:
                self.process_token( _Newline() )
                self.write_indent( self.block_mode[-1] )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            if not self.newline:
                self.process_token( _Newline() )
                self.write_indent( self.block_mode[-1] )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def end_line(self):
        if self.block_mode[-1]["type"] == "oneline":
            self.process_token( _Symbol(';') )
            self.process_token( _Whitespace(1) )
        elif self.block_mode[-1]["type"] == "toplevel":
            self.process_token( _Newline() )
        elif self.block_mode[-1]["type"] == "indent":
            self.process_token( _Newline() )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            self.process_token( _Newline() )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def get_min_indent(self):
        mindent = None
        for mode in self.block_mode:
            if "indent" in mode:
                mindent = mode
        return mindent

    def inc_indent(self):
        mindent = self.get_min_indent()
        indent = mindent["indent"]
        a2 = random.random()
        if a2 < 0.5:
            indent += ' '
        else:
            indent += '\t'
        return indent

    def write_indent(self, mode):
        if "indent" not in mode:
            raise Exception("no indent", mode)
        self.raw_write( mode["indent"] )
class Unparse(object):

    def subshape( node ):
        yield _BeginNode(node)
        yield from node.shape()
        yield _EndNode(node)
    class Toplevel(object):
        def shape(self):
            yield _BeginNode(self)
            yield _Line()
            for leaf in self.leaves:
                yield from Unparse.subshape( leaf )
            yield _EndNode(self)
            
    class TextNode(object):
        def shape(self):
            yield from [ _Line(), _Exact(self.text) ]

    class ObjectBlock(object):
        def shape(self):
            yield from [_BeginLine(), _Line() ]
            if self.parent is None:
                yield from [ _Symbol("/"), _Fuzz() ]
            yield from [ _Ident(self.name), _Fuzz() ]
            if len(self.leaves) == 1 and self.leaves[0].join_path:
                yield from [ _Symbol("/"), _Fuzz() ]
                yield from Unparse.subshape( self.leaves[0] )
                yield _EndLine()
            else:
                yield _BeginBlock()
                for leaf in self.leaves:
                    yield from Unparse.subshape( leaf )
                yield _EndBlock() 
                yield _EndLine()

    class GlobalVarDefine(object):
        def shape(self):
            yield from [_BeginLine(), _Line(), _Fuzz(), _Keyword("var"), _Fuzz(), _Symbol("/"), _Fuzz() ]
            for seg in self.var_path:
                yield from [ _Ident(seg, "path"), _Fuzz(), _Symbol("/"), _Fuzz() ]
            yield from [ _Ident( self.name, "name" ) ]
            if self.expression is not None:
                yield from [ _Whitespace(1), _Symbol("="), _Whitespace(1) ]
                yield from Unparse.subshape( self.expression )
            yield _EndLine()
    class ObjectVarDefine(object):
        def shape(self):
            if len(self.parent.leaves) != 1:
                yield _BeginLine()
            yield _Line()
            if not self.is_override:
                yield from [_Fuzz(), _Keyword("var"), _Fuzz(), _Symbol("/"), _Fuzz()]
                for seg in self.var_path:
                    yield from [ _Ident(seg, "path"), _Fuzz(), _Symbol("/"), _Fuzz() ]
            yield from [ _Ident( self.name, "name" ), _Fuzz() ]
            if self.expression is not None:
                yield from [ _Whitespace(1), _Symbol("="), _Whitespace(1) ]
                yield from Unparse.subshape( self.expression )
            if len(self.parent.leaves) != 1:
                yield _EndLine()

    class ObjectProcDefine(object):
        def shape(self):
            if len(self.parent.leaves) != 1:
                yield _BeginLine()
            yield _Line()
            if not self.is_override:
                yield from [_Keyword("proc"), _Symbol("/"), _Fuzz()]
            yield from [_Ident(self.name, "name"), _Fuzz(), _BeginParen(), _Whitespace()]
            for param in self.params:
                yield from Unparse.subshape( param )
            yield from [_EndParen(), _BeginBlock() ]
            for stmt in self.body:
                yield from Unparse.subshape( stmt )
            yield _EndBlock()
            if len(self.parent.leaves) != 1:
                yield _EndLine()

    class GlobalProcDefine(object):
        def shape(self):
            yield from [_BeginLine(), _Line(), _Symbol("/"), _Fuzz(), _Ident("proc"), _Fuzz(), _Symbol("/"), _Fuzz()]
            yield from [_Ident(self.name, "name"), _Fuzz(), _BeginParen(), _Whitespace()]
            for param in self.params:
                yield from Unparse.subshape( param )
            yield from [_EndParen(), _BeginBlock() ]
            for stmt in self.body:
                yield from Unparse.subshape( stmt )
            yield _EndBlock()
            yield _EndLine()
    class ProcArgument(object):
        def shape(self):
            yield _Line()
            if self.param_type is not None:
                yield from Unparse.subshape( self.param_type )
            yield from [_Ident(self.name, "name"), _Whitespace()]
            if self.default is not None:
                yield from [_Symbol("="), _Whitespace()]
                yield from Unparse.subshape( self.default )
            if self.possible_values is not None:
                yield from [_Keyword("as"), _Whitespace()]
                yield from Unparse.subshape( self.possible_values )

    class Stmt(object):
        class Expression(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()
                
        class VarDefine(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("var"), _Fuzz(), _Symbol("/"), _Fuzz()]
                if self.var_type is not None:
                    yield from Unparse.subshape( self.var_type )
                yield from [_Ident(self.name, "name")]
                if self.expr is not None:
                    yield from [_Whitespace(1), _Symbol("="), _Whitespace(1) ]
                    yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Return(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("return"), _Whitespace(1)]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

            def default_ws(self):
                return [ "\n", "", " ", "", "\n" ]

        class Break(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("break"), _Whitespace(1), _Ident(self.label, "label"), _Fuzz()]
                yield _EndLine()

        class Continue(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("continue"), _Whitespace(1), _Ident(self.label, "label"), _Fuzz()]
                yield _EndLine()

        class Goto(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("goto"), _Whitespace(1), _Ident(self.label, "label"), _Fuzz()]
                yield _EndLine()

        class Label(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Ident(self.label, "label"), _Fuzz()]
                if self.has_colon:
                    yield from [_Symbol(":"), _Fuzz()]
                yield _BeginBlock()
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class Del(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("del"), _Whitespace(1) ]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Set(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("set"), _Whitespace(1), _Ident(self.attr, "attr"), _Whitespace(), _Symbol("="), _Whitespace()]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Spawn(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword["spawn"], _Fuzz(), _BeginParen(), _Whitespace() ]
                yield from Unparse.subshape( self.delay )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class If(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword["if"], _Fuzz(), _BeginParen(), _Whitespace() ]
                yield from Unparse.subshape( self.condition )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for stmt in self.truebody:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                if self.falsebody is not None:
                    yield from [_Keyword["else"], _Whitespace(), _BeginBlock() ]
                    for stmt in self.falsebody:
                        yield from Unparse.subshape( stmt )
                    yield _EndBlock()
                yield _EndLine()

        class For(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword["for"], _Fuzz(), _BeginParen(), _Whitespace() ]
                if self.expr1 is not None:
                    yield from Unparse.subshape( self.expr1 )
                    yield from [_Symbol(";"), _Whitespace()]
                if self.expr2 is not None:
                    yield from Unparse.subshape( self.expr2 )
                    yield from [_Symbol(";"), _Whitespace()]
                if self.expr3 is not None:
                    yield from Unparse.subshape( self.expr3 )
                yield from [_EndParen(), _Fuzz(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class ForEnumerator(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("for"), _Fuzz(), _BeginParen(), _Whitespace()]
                yield from Unparse.subshape( self.var_expr )
                yield from [_Whitespace(1), _Keyword("in"), _Whitespace()]
                yield from Unparse.subshape( self.list_expr )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class While(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("while"), _Fuzz(), _BeginParen(), _Whitespace()]
                yield from Unparse.subshape( self.condition )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class DoWhile(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword["do"], _Fuzz(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield from [_EndBlock(), _Fuzz()]
                yield from [_Keyword("while"), _Fuzz(), _BeginParen(), _Whitespace()]
                yield from Unparse.subshape( self.condition )
                yield from [_EndParen(), _Whitespace()]
                yield _EndLine()

        class Switch(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("switch"), _Fuzz(), _BeginParen(), _Whitespace()]
                yield from Unparse.subshape( self.switch_expr )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for case in self.cases:
                    Unparse.subshape( case )
                yield _EndBlock()
                yield _EndLine()

            class IfCase(object):
                def shape(self):
                    yield from [_BeginLine(), _Line()]
                    yield from [_Keyword("if"), _Fuzz(), _BeginParen(), _Whitespace()]
                    yield from Unparse.subshape( self.condition )
                    yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                    for stmt in self.stmts:
                        yield from Unparse.subshape( stmt )
                    yield _EndBlock()
                    yield _EndLine()

            class ElseCase(object):
                def shape(self):
                    yield from [_BeginLine(), _Line()]
                    yield from [_Keyword("else"), _Whitespace(1), _BeginBlock()]
                    for stmt in self.stmts:
                        yield from Unparse.subshape( stmt )
                    yield _EndBlock()
                    yield _EndLine()

        class Try(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("try"), _BeginBlock()]
                for stmt in self.try_body:
                    yield from Unparse.subshape( stmt )
                yield from [_EndBlock(), _EndLine(), _BeginLine(), _Keyword("catch"), _Whitespace(), _BeginParen(), _Whitespace() ]
                yield from Unparse.subshape( self.catch_param )
                yield from [_EndParen(), _Whitespace(1), _BeginBlock()]
                for stmt in self.catch_body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

            class Catch(object):
                def shape(self):
                    yield from [_Line()]
                    yield from Unparse( self.expr )

        class Throw(object):
            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("throw"), _Whitespace(1) ]
                yield from Unparse( self.expr )
                yield _EndLine()

    class Expr(object):
        class Identifier(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Ident(self.name), _Fuzz()]

        class GlobalIdentifier(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Exact("global."), _Ident(self.name), _Fuzz()]
                
        class Integer(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Exact(str(self.n)), _Fuzz()]

        class Float(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Exact(str(self.n)), _Fuzz()]
                
        class String(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol('"'), _Exact(str(self.s)), _Symbol('"'), _Fuzz()]

        class FormatString(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                i = 0
                while i < len(self.exprs):
                    yield from [_Symbol('"'), _Exact(str(self.strings[i])), _Symbol('['), _Whitespace(1) ] 
                    yield from Unparse.subshape( self.exprs[i])
                    yield from [_Whitespace(1), _Symbol("]")]
                    i += 1
                yield from [_Exact(str(self.strings[i])), _Symbol('"'), _Fuzz()]

        class Resource(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol("'"), _Exact(str(self.s)), _Symbol("'"), _Fuzz()]

        class Null(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Exact("null"), _Fuzz()]

        class Property(object):
            def shape(self):
                yield from [_Line(), _Exact(self.name), _Fuzz()]

        class Path(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                if self.prefix is not None:
                    yield _Symbol(self.prefix)
                i = 0
                while i < len(self.ops):
                    yield from [ _Ident(self.types[i], "path"), _Symbol(self.ops[i])]
                    i += 1
                yield from [_Ident(self.types[i], "path"), _Fuzz()]

        class Call(object):
            class Identifier(object):
                def shape(self):
                    yield from [_Fuzz(), _Line()]
                    yield from [_Ident(self.name, "call"), _Fuzz(), _BeginParen(), _Whitespace()]
                    for arg in self.args:
                        yield from Unparser.subshape(arg)
                    yield from [_Whitespace(), _EndParen()]

            class Expr(object):
                def shape(self):
                    yield from [_Fuzz(), _Line()]
                    yield from Unparser.subshape( self.expr )
                    yield from [_Ident(self.name, "call"), _Fuzz(), _BeginParen(), _Whitespace()]
                    for arg in self.args:
                        yield from Unparser.subshape(arg)
                    yield from [_Whitespace(), _EndParen()]

            class Param(object):
                def shape(self):
                    yield from [_Fuzz(), _Line()]
                    if self.name is not None:
                        yield from [_Ident(self.name, "param"), _Whitespace(1), _Symbol("="), _Whitespace(1)]
                    yield from Unparser.subshape( self.value )
        class Super(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Exact(".."), _Fuzz()]

        class Self(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Exact("."), _Fuzz()]

    @staticmethod
    def op_shape(self):
        yield _Line()
        if self.parent and self.parent.prec >= self.prec:
            yield from [_Fuzz(), _Symbol("("), _Fuzz() ]
        cleaf = 0
        for e in self.fixity:
            if e == "_":
                yield from Unparse.subshape( self.exprs[cleaf] )
                cleaf += 1
            elif type(e) is str:
                if self.spacing:
                    yield from [_Whitespace(1), _Symbol(e), _Whitespace(1)]
                else:
                    yield from [_Fuzz(), _Symbol(e), _Fuzz()]
            else:
                raise Exception("bad fixity")
        if self.parent and self.parent.prec >= self.prec:
            yield from [_Fuzz(), _Symbol(")"), _Fuzz() ]

    def initialize():
        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            ty.join_path = False

        AST.ObjectBlock.join_path = True
        AST.ObjectVarDefine.join_path = True
        AST.ObjectProcDefine.join_path = True

        for ty in Shared.Type.iter_types(AST.Op):
            if ty is AST.Op:
                continue
            if not hasattr('ty', 'shape'):
                ty.shape = Unparse.op_shape
            ty.spacing = True

        for ty in Shared.Type.iter_types(AST.Expr):
            if ty is AST.Expr:
                continue
            ty.spacing = True

        for ty_name in ["PathUpwards", "PathDownwards", "PathBranch", "Deref", "MaybeDeref", "LaxDeref", "MaybeLaxDeref", "Index", "MaybeIndex"]:
            op = getattr(AST.Op, ty_name)
            op.spacing = False

        Shared.Type.mix_fn(AST, Unparse, 'shape')

Unparse.initialize()