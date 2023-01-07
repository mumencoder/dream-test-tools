
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
def _Keyword(text):
    return {"type":"Keyword", "text":text}
def _Ident(text, type=None):
    return {"type":"Ident", "text":text, "id_type":type}
def _Text(text, type=None):
    return {"type":"Text", "text":text, "text_type":type}
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
 
    def update_mode(self, token):
        if token["type"] == "BeginNode":
            self.node_stack.append( token["node"] )
        if token["type"] == "EndNode":
            self.node_stack.pop()

        if token["type"] == "Line":
            node = self.node_stack[-1]
            if not hasattr(node, 'lineno'):
                node.lineno = self.current_line

        if token["type"] == "Newline":
            self.current_line += 1

    def raw_write(self, s):
        self.s.write(s)

    def fuzz_shape(self, shape):
        return self.coalesce_newlines( self.fuzz_stream( shape ) )

    def unparse(self, tokens):
        for token in self.strip_nonprintable( self, tokens ):
            self.write_token( token )

    def fuzz_stream(self, tokens):
        for token in tokens:
            yield from self.fuzz_token(token)

    def coalesce_newlines(self, tokens):
        newline = True
        for token in tokens:
            if token["type"] == "Newline":
                if newline is True:
                    pass
                else:
                    yield token
                newline = True
            elif token["type"] in ["Text", "Symbol", "Keyword", "Ident", "Whitespace"]:
                newline = False
                yield token
            elif token["type"] in ["BeginNode", "EndNode", "Line"]:
                yield token
            else:
                raise Exception("unknown token", token)

    def strip_nonprintable(self, tokens):
        for token in tokens:
            self.update_mode(token)
            if token["type"] in ["Text", "Symbol", "Ident", "Keyword", "Newline"]:
                yield token
            else:
                pass

    def fuzz_indent(self, mode):
        if "indent" not in mode:
            raise Exception("no indent", mode)
        yield _Text( mode["indent"], type="indent" )
    
    def fuzz_token(self, token):
        if token["type"] == "Fuzz":
            pass
        elif token["type"] == "BeginBlock":
            # TODO: check for single leafs in node
            if self.block_mode[-1]["type"] == "oneline":
                self.block_mode.append( {"type":"oneline"} )
            else:
                a = random.random()
                if a < 0.05:
                    self.block_mode.append( {"type":"oneline"} )
                elif a < 0.66:
                    self.block_mode.append( {"type":"indent", "indent": self.inc_indent()} )
                else:
                    self.block_mode.append( {"type":"nice_bracket", "indent": self.inc_indent()})
            yield from self.begin_block()
        elif token["type"] == "EndBlock":
            yield from self.end_block()
            self.block_mode.pop()
        elif token["type"] == "BeginLine":
            yield from self.begin_line()
        elif token["type"] == "EndLine":
            yield from self.end_line()
        elif token["type"] == "BeginParen":
            yield _Symbol('(')
        elif token["type"] == "EndParen":
            yield _Symbol(')')
        elif token["type"] == "Whitespace":
            if token["n"] == 0:
                a = random.random()
                if a < 0.5:
                    yield _Text(" ", type="ws")
            elif token["n"] == 1:
                a = random.random()
                if a < 0.95:
                    yield _Text(" ", type="ws")
            else:
                raise Exception(token)
        else:
            yield token

    def write_token(self, token):
        if token["type"] == "Text":
            self.raw_write( token["text"] )
        elif token["type"] == "Symbol":
            self.raw_write( token["text"] )
        elif token["type"] == "Ident":
            self.raw_write( token["text"] )
        elif token["type"] == "Keyword":
            self.raw_write( token["text"] )
        elif token["type"] == "Newline":
            self.raw_write('\n')
        else:
            raise Exception("unknown token", token)

    def begin_block(self):
        if self.block_mode[-1]["type"] == "oneline":
            yield from self.fuzz_token( _Whitespace() )
            yield from self.fuzz_token( _Symbol('{') )
            yield from self.fuzz_token( _Whitespace(1) )
        elif self.block_mode[-1]["type"] == "indent":
            yield from self.fuzz_token( _Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( _Whitespace() )
            yield from self.fuzz_token( _Symbol('{') )
            yield from self.fuzz_token( _Fuzz() )
            yield from self.fuzz_token( _Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def end_block(self):
        if self.block_mode[-1]["type"] == "oneline":
            yield from self.fuzz_token( _Symbol('}') )
            yield from self.fuzz_token( _Whitespace(1) )
        elif self.block_mode[-1]["type"] == "indent":
            pass
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( _Newline() )
            yield from self.fuzz_indent( self.block_mode[-2] )
            yield from self.fuzz_token( _Symbol('}') )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def begin_line(self):
        if self.block_mode[-1]["type"] == "oneline":
            pass
        elif self.block_mode[-1]["type"] == "toplevel":
            pass
        elif self.block_mode[-1]["type"] == "indent":
            yield from self.fuzz_token( _Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( _Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def end_line(self):
        if self.block_mode[-1]["type"] == "oneline":
            yield from self.fuzz_token( _Symbol(';') )
            yield from self.fuzz_token( _Whitespace(1) )
        elif self.block_mode[-1]["type"] == "toplevel":
            yield from self.fuzz_token( _Newline() )
        elif self.block_mode[-1]["type"] == "indent":
            yield from self.fuzz_token( _Newline() )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( _Newline() )
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

    def marshall_tokens(tokens):
        result = []
        for token in tokens:
            if token["type"] == "BeginNode":
                result.append( {"type":"BeginNode", "node": id(token["node"])} )
            elif token["type"] == "EndNode":
                result.append( {"type":"EndNode", "node": id(token["node"])} )
            else:
                result.append( dict(token) )
        return result

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
            yield from [ _Line(), _Text(self.text, type="general") ]

    class ObjectBlock(object):
        def shape(self):
            yield from [_BeginLine(), _Line() ]
            if self.parent is None:
                yield from [ _Symbol("/"), _Fuzz() ]
            yield from [ _Ident(self.name), _Fuzz() ]
            if len(self.leaves) == 1 and self.leaves[0].can_join_path and self.leaves[0].should_join_path:
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
                if self.is_verb:
                    proc_type = _Keyword("verb")
                else:
                    proc_type = _Keyword("proc")
                yield from [proc_type, _Symbol("/"), _Fuzz()]
            yield from [_Ident(self.name, "name"), _Fuzz(), _BeginParen(), _Whitespace()]
            for i, param in enumerate(self.params):
                yield from Unparse.subshape( param )
                if i < len(self.params) - 1:
                    yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
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
            for i, param in enumerate(self.params):
                yield from Unparse.subshape( param )
                if i < len(self.params) - 1:
                    yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
            yield from [_EndParen(), _BeginBlock() ]
            for stmt in self.body:
                yield from Unparse.subshape( stmt )
            yield _EndBlock()
            yield _EndLine()
    class ProcArgument(object):
        def shape(self):
            yield _Line()
            if self.path_type is not None:
                yield from Unparse.subshape( self.path_type )
                yield from [_Fuzz(), _Symbol("/")]
            yield _Ident(self.name, "name")
            if self.default is not None:
                yield from [_Whitespace(1), _Symbol("="), _Whitespace(1)]
                yield from Unparse.subshape( self.default )
            if self.possible_values is not None:
                yield from [_Whitespace(1), _Keyword("as"), _Whitespace(1)]
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
                yield from [_Fuzz(), _Line(), _Text("global.", type="global_id"), _Ident(self.name), _Fuzz()]
                
        class Integer(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Text(str(self.n), type="int"), _Fuzz()]

        class Float(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Text(str(self.n), type="float"), _Fuzz()]
                
        class String(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol('"'), _Text(str(self.s), type="string"), _Symbol('"'), _Fuzz()]

        class FormatString(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol('"')]
                i = 0
                while i < len(self.exprs):
                    yield from [_Text(str(self.strings[i]), type="fmt_string"), _Symbol('['), _Whitespace(1) ] 
                    yield from Unparse.subshape( self.exprs[i])
                    yield from [_Whitespace(1), _Symbol("]")]
                    i += 1
                yield from [_Text(str(self.strings[i]), type="fmt_string"), _Symbol('"'), _Fuzz()]

        class Resource(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol("'"), _Text(str(self.s), type="resource"), _Symbol("'"), _Fuzz()]

        class Null(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Text("null", type="null"), _Fuzz()]

        class Property(object):
            def shape(self):
                yield from [_Line(), _Text(self.name, type="property"), _Fuzz()]

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
            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from Unparse.subshape( self.expr )
                yield from [_Fuzz(), _BeginParen(), _Whitespace()]
                for i, arg in enumerate(self.args):
                    yield from Unparse.subshape(arg)
                    if i < len(self.args) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
                yield from [_Whitespace(), _EndParen()]

            class Param(object):
                def shape(self):
                    yield from [_Fuzz(), _Line()]
                    if self.name is not None:
                        yield from [_Ident(self.name, "param"), _Whitespace(1), _Symbol("="), _Whitespace(1)]
                    yield from Unparse.subshape( self.value )

        class Super(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Text("..", type="super"), _Fuzz()]

        class Self(object):
            def shape(self):
                yield from [_Fuzz(), _Line(), _Text(".", type="self"), _Fuzz()]

        class Input(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from [_Text("input", type="proclike"), _Fuzz()]
                yield from [_Whitespace(), _BeginParen(), _Whitespace(1)]
                for i, arg in enumerate(self.args):
                    yield from Unparse.subshape(arg)
                    if i < len(self.args) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
                yield from [_Whitespace(), _EndParen()]
                if self.as_type is not None:
                    yield from [_Whitespace(1), _Keyword("as"), _Whitespace(1), _Ident(self.as_type)]
                if self.in_list is not None:
                    yield from [_Whitespace(1), _Keyword("in"), _Whitespace(1)]
                    yield from Unparse.subshape(self.in_list)

        class AsType(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                for i, flag in enumerate(self.flags):
                    yield _Text(flag, type="asflag")
                    if i < len(self.flags) - 1:
                        yield from [_Whitespace(1), _Symbol('|'), _Whitespace(1)]

        class ModifiedType(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from Unparse.subshape(self.path)
                yield from [_Whitespace(), _Symbol("{"), _Whitespace(1)]
                for i, mod in enumerate(self.mods):
                    yield _Ident(mod.var)
                    yield from [_Whitespace(1), _Symbol('='), _Whitespace(1)]
                    yield from Unparse.subshape(mod.val)
                    if i < len(self.mods) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
                yield from [_Whitespace(1), _Symbol('}')]

        class Pick(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from [_Text("pick", type='proclike')]
                yield from [_Whitespace(), _BeginParen(), _Whitespace(1)]
                for i, option in enumerate(self.options):
                    yield from Unparse.subshape(option.p)
                    yield from [_Whitespace(1), _Symbol(';'), _Whitespace(1)]
                    yield from Unparse.subshape(option.val)
                    if i < len(self.options) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
                yield from [_Whitespace(), _EndParen()]
                
        class New(object):
            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from [_Text("new", type="proclike")]                
                yield from [_Whitespace(), _BeginParen(), _Whitespace(1)]
                for i, arg in enumerate(self.args):
                    yield from Unparse.subshape(arg)
                    if i < len(self.args) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]    
                yield from [_Whitespace(), _EndParen()]

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
            ty.can_join_path = False

        AST.ObjectBlock.can_join_path = True
        AST.ObjectVarDefine.can_join_path = True
        AST.ObjectProcDefine.can_join_path = True

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