
from ..common import *

from .dmast import *
from .Shape import *

class Unparser(object):
    def __init__(self, env):
        self.env = env
        self.s = io.StringIO()

    def raw_write(self, s):
        self.s.write(s)

    def unparse(self):
        for token in Shape.strip_nonprintable( self.env.attr.collider.ast_tokens ):
            self.write_token( token )
        return self.s.getvalue()

    def write_token(self, token):
        if token["type"] == "Text":
            self.raw_write( token["text"] )
        elif token["type"] == "Symbol":
            self.raw_write( token["text"] )
        elif token["type"] == "Keyword":
            self.raw_write( token["text"] )
        elif token["type"] == "Newline":
            self.raw_write('\n')
        else:
            raise Exception("unknown token", token)

_Line = Shape.Line
_BeginNode = Shape.BeginNode
_EndNode = Shape.EndNode
_Keyword = Shape.Keyword
_Symbol = Shape.Symbol
_Text = Shape.Text
_BeginParen = Shape.BeginParen
_EndParen = Shape.EndParen
_Whitespace = Shape.Whitespace
_BeginBlock = Shape.BeginBlock
_EndBlock = Shape.EndBlock
_BeginLine = Shape.BeginLine
_EndLine = Shape.EndLine
_Fuzz = Shape.Fuzz

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
        def tokens_used():
            return ["general"]

        def shape(self):
            yield from [ _Line(), _Text(self.text, type="general") ]

    class ObjectPath(object):
        def tokens_used():
            return ["/", ".", ":", "name", "var", "proc", "verb"]

        def shape(self):
            for segment in self.segments:
                if segment in ["/", ".", ":"]:
                    yield _Symbol(segment)
                elif segment in ["var", "proc", "verb"]:
                    yield _Keyword(segment)
                else:
                    yield _Text(segment, "name")

    class ObjectBlock(object):
        def tokens_used():
            return []

        def shape(self):
            yield from [_BeginLine(), _Line() ]
            yield from Unparse.subshape( self.path )
            yield _BeginBlock()
            for leaf in self.leaves:
                yield from Unparse.subshape( leaf )
            yield _EndBlock() 
            yield _EndLine()

    class ObjectVarDefine(object):
        def tokens_used():
            return ["=", "varname"]

        def shape(self):
            # TODO: ability to supress BeginLine if this is the only leaf of the ObjectBlock
            yield from [_BeginLine(), _Line()]
            yield _Text(self.name, "varname")
            if self.expression is not None:
                yield from [ _Whitespace(1), _Symbol("="), _Whitespace(1) ]
                yield from Unparse.subshape( self.expression )
    class ProcDefine(object):
        def tokens_used():
            return [",", "procname"]

        def shape(self):
            # TODO: ability to supress BeginLine if this is the only leaf of the ObjectBlock
            yield from [_BeginLine(), _Line()]
            yield _Text(self.name, "procname")
            yield from [_Fuzz(), _BeginParen(), _Whitespace()]
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
        def tokens_used():
            return ["/", "=", "name", "as"]

        def shape(self):
            yield _Line()
            if self.path_type is not None:
                yield from Unparse.subshape( self.path_type )
                yield from [_Fuzz(), _Symbol("/")]
            yield _Text(self.name, "name")
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
            def tokens_used():
                return ["/", "=", "name", "var"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("var"), _Fuzz(), _Symbol("/"), _Fuzz()]
                if self.var_type is not None:
                    for segment in self.var_type:
                        yield from [_Text(segment, "path"), _Fuzz(), _Symbol("/"), _Fuzz()]
                yield from [_Text(self.name, "name")]
                if self.expr is not None:
                    yield from [_Whitespace(1), _Symbol("="), _Whitespace(1) ]
                    yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Return(object):
            def tokens_used():
                return ["return"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("return"), _Whitespace(1)]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Break(object):
            def tokens_used():
                return ["break", "label"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("break"), _Whitespace(1), _Text(self.label, "label"), _Fuzz()]
                yield _EndLine()

        class Continue(object):
            def tokens_used():
                return ["continue", "label"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("continue"), _Whitespace(1), _Text(self.label, "label"), _Fuzz()]
                yield _EndLine()

        class Goto(object):
            def tokens_used():
                return ["goto", "label"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("goto"), _Whitespace(1), _Text(self.label, "label"), _Fuzz()]
                yield _EndLine()

        class Label(object):
            def tokens_used():
                return [":", "label"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Text(self.name, "label"), _Fuzz()]
                if self.has_colon:
                    yield from [_Symbol(":"), _Fuzz()]
                yield _BeginBlock()
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class Del(object):
            def tokens_used():
                return ["del"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("del"), _Whitespace(1) ]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Set(object):
            def tokens_used():
                return ["set", "attr", "="]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("set"), _Whitespace(1), _Text(self.attr, "attr"), _Whitespace(), _Symbol("="), _Whitespace()]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

        class Spawn(object):
            def tokens_used():
                return ["spawn"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("spawn"), _Fuzz(), _BeginParen(), _Whitespace() ]
                yield from Unparse.subshape( self.delay )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                yield _EndLine()

        class If(object):
            def tokens_used():
                return ["if", "else"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("if"), _Fuzz(), _BeginParen(), _Whitespace() ]
                yield from Unparse.subshape( self.condition )
                yield from [_EndParen(), _Whitespace(), _BeginBlock()]
                for stmt in self.truebody:
                    yield from Unparse.subshape( stmt )
                yield _EndBlock()
                if self.falsebody is not None:
                    yield from [_Keyword("else"), _Whitespace(), _BeginBlock() ]
                    for stmt in self.falsebody:
                        yield from Unparse.subshape( stmt )
                    yield _EndBlock()
                yield _EndLine()

        class For(object):
            def tokens_used():
                return ["for", ";"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("for"), _Fuzz(), _BeginParen(), _Whitespace() ]
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
            def tokens_used():
                return ["for", "in"]

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
            def tokens_used():
                return ["while"]

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
            def tokens_used():
                return ["do", "while"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("do"), _Fuzz(), _BeginBlock()]
                for stmt in self.body:
                    yield from Unparse.subshape( stmt )
                yield from [_EndBlock(), _Fuzz()]
                yield from [_Keyword("while"), _Fuzz(), _BeginParen(), _Whitespace()]
                yield from Unparse.subshape( self.condition )
                yield from [_EndParen(), _Whitespace()]
                yield _EndLine()

        class Switch(object):
            def tokens_used():
                return ["switch"]

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
                def tokens_used():
                    return ["if"]

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
                def tokens_used():
                    return ["else"]

                def shape(self):
                    yield from [_BeginLine(), _Line()]
                    yield from [_Keyword("else"), _Whitespace(1), _BeginBlock()]
                    for stmt in self.stmts:
                        yield from Unparse.subshape( stmt )
                    yield _EndBlock()
                    yield _EndLine()

        class Try(object):
            def tokens_used():
                return ["try", "catch"]

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
                    yield from Unparse.subshape( self.expr )

        class Throw(object):
            def tokens_used():
                return ["throw"]

            def shape(self):
                yield from [_BeginLine(), _Line()]
                yield from [_Keyword("throw"), _Whitespace(1) ]
                yield from Unparse.subshape( self.expr )
                yield _EndLine()

    class Expr(object):
        class Identifier(object):
            def tokens_used():
                return ["ident"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Text(self.name, "ident"), _Fuzz()]

        class GlobalIdentifier(object):
            def tokens_used():
                return ["global_id", "ident"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Text("global.", "global_id"), _Text(self.name, "ident"), _Fuzz()]
                
        class Integer(object):
            def tokens_used():
                return ["int"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Text(str(self.n), "int"), _Fuzz()]

        class Float(object):
            def tokens_used():
                return ["float"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Text(str(self.n), "float"), _Fuzz()]
                
        class String(object):
            def tokens_used():
                return ['"', "string"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol('"'), _Text(str(self.s), "string"), _Symbol('"'), _Fuzz()]

        class FormatString(object):
            def tokens_used():
                return ['"', "[", "]", "fmt_string"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol('"')]
                i = 0
                while i < len(self.exprs):
                    yield from [_Text(str(self.strings[i]), "fmt_string"), _Symbol('['), _Whitespace(1) ] 
                    yield from Unparse.subshape( self.exprs[i])
                    yield from [_Whitespace(1), _Symbol("]")]
                    i += 1
                yield from [_Text(str(self.strings[i]), "fmt_string"), _Symbol('"'), _Fuzz()]

        class Resource(object):
            def tokens_used():
                return ["'", "resource"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol("'"), _Text(str(self.s), "resource"), _Symbol("'"), _Fuzz()]

        class Null(object):
            def tokens_used():
                return ["null"]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Text("null", "null"), _Fuzz()]

        class Property(object):
            def tokens_used():
                return ["property"]

            def shape(self):
                yield from [_Line(), _Text(self.name, "property"), _Fuzz()]

        class Path(object):
            def tokens_used():
                return [".", ":", "/", "path"]

            def shape(self):
                yield from [_Fuzz(), _Line()]
                for segment in self.segments:
                    if segment in [".", ":", "/"]:
                        yield _Symbol(segment)
                    else:
                        yield _Text(segment, "path")

        class Call(object):
            def tokens_used():
                return [","]

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
                def tokens_used():
                    return ["=", "param"]

                def shape(self):
                    yield from [_Fuzz(), _Line()]
                    if self.name is not None:
                        yield from [_Text(self.name, "param"), _Whitespace(1), _Symbol("="), _Whitespace(1)]
                    yield from Unparse.subshape( self.value )

        class Super(object):
            def tokens_used():
                return [".."]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol(".."), _Fuzz()]

        class Self(object):
            def tokens_used():
                return ["."]

            def shape(self):
                yield from [_Fuzz(), _Line(), _Symbol("."), _Fuzz()]

        class Input(object):
            def tokens_used():
                return [",", "proclike", "as", "in", "asflag"] 

            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from [_Text("input", "proclike"), _Fuzz()]
                yield from [_Whitespace(), _BeginParen(), _Whitespace(1)]
                for i, arg in enumerate(self.args):
                    yield from Unparse.subshape(arg)
                    if i < len(self.args) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
                yield from [_Whitespace(), _EndParen()]
                if self.as_type is not None:
                    yield from [_Whitespace(1), _Keyword("as"), _Whitespace(1), _Text(self.as_type, "asflag")]
                if self.in_list is not None:
                    yield from [_Whitespace(1), _Keyword("in"), _Whitespace(1)]
                    yield from Unparse.subshape(self.in_list)

        class AsType(object):
            def tokens_used():
                return ["|", "asflag"]

            def shape(self):
                yield from [_Fuzz(), _Line()]
                for i, flag in enumerate(self.flags):
                    yield _Text(flag, "asflag")
                    if i < len(self.flags) - 1:
                        yield from [_Whitespace(1), _Symbol('|'), _Whitespace(1)]

        class ModifiedType(object):
            def tokens_used():
                return ["{", "=", ",", "}", "varname"]

            def shape(self):
                yield from [_Fuzz(), _Line()]
                yield from Unparse.subshape(self.path)
                yield from [_Whitespace(), _Symbol("{"), _Whitespace(1)]
                for i, mod in enumerate(self.mods):
                    yield _Text(mod.var, "varname")
                    yield from [_Whitespace(1), _Symbol('='), _Whitespace(1)]
                    yield from Unparse.subshape(mod.val)
                    if i < len(self.mods) - 1:
                        yield from [_Whitespace(1), _Symbol(','), _Whitespace(1)]
                yield from [_Whitespace(1), _Symbol('}')]

        class Pick(object):
            def tokens_used():
                return [";", ",", "proclike"]

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
            def tokens_used():
                return [",", "proclike"]

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
    def op_tokens_used(ty):
        tokens = []
        for e in ty.fixity:
            if e == "_":
                continue
            if type(e) is str:
                tokens.append( e )
        return tokens

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
        AST.ProcDefine.can_join_path = True

        for ty in Shared.Type.iter_types(AST.Op):
            if ty is AST.Op:
                continue
            if not hasattr(ty, 'shape'):
                ty.shape = Unparse.op_shape
            if not hasattr(ty, 'tokens_used'):
                ty.tokens_used = lambda ty=ty: Unparse.op_tokens_used(ty)
            ty.spacing = True

        for ty in Shared.Type.iter_types(AST.Expr):
            if ty is AST.Expr:
                continue
            ty.spacing = True

        for ty_name in ["PathUpwards", "PathDownwards", "PathBranch", "Deref", "MaybeDeref", "LaxDeref", "MaybeLaxDeref", "Index", "MaybeIndex"]:
            op = getattr(AST.Op, ty_name)
            op.spacing = False

        Shared.Type.mix_fn(AST, Unparse, 'shape')
        Shared.Type.mix_fn(AST, Unparse, 'tokens_used')

        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            if not hasattr(ty, 'tokens_used'):
                ty.tokens_used = lambda: []        

        from . import NGram
        NGram.calculate_ordinals()

Unparse.initialize()