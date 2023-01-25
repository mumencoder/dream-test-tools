
from ..common import *
from .Shape import *

class Fuzzer(object):
    def __init__(self):
        self.block_mode = [ {"type":"toplevel", 'indent':''} ]

    def fuzz_shape(self, shape):
        return self.fuzz_stream( shape )

    def fuzz_stream(self, tokens):
        si = ShapeIter(tokens)
        for token in si:
            yield from self.fuzz_token(token)

    def fuzz_indent(self, mode):
        if "indent" not in mode:
            raise Exception("no indent", mode)
        yield Shape.Text( mode["indent"], "indent" )
    
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
            yield Shape.Symbol('(')
        elif token["type"] == "EndParen":
            yield Shape.Symbol(')')
        elif token["type"] == "Whitespace":
            if token["n"] == 0:
                a = random.random()
                if a < 0.5:
                    yield Shape.Text(" ", type="ws")
            elif token["n"] == 1:
                a = random.random()
                if a < 0.95:
                    yield Shape.Text(" ", type="ws")
            else:
                raise Exception(token)
        else:
            yield token

    def begin_block(self):
        if self.block_mode[-1]["type"] == "oneline":
            yield from self.fuzz_token( Shape.Whitespace() )
            yield from self.fuzz_token( Shape.Symbol('{') )
            yield from self.fuzz_token( Shape.Whitespace(1) )
        elif self.block_mode[-1]["type"] == "indent":
            yield from self.fuzz_token( Shape.Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( Shape.Whitespace() )
            yield from self.fuzz_token( Shape.Symbol('{') )
            yield from self.fuzz_token( Shape.Fuzz() )
            yield from self.fuzz_token( Shape.Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def end_block(self):
        if self.block_mode[-1]["type"] == "oneline":
            yield from self.fuzz_token( Shape.Symbol('}') )
            yield from self.fuzz_token( Shape.Whitespace(1) )
        elif self.block_mode[-1]["type"] == "indent":
            pass
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( Shape.Newline() )
            yield from self.fuzz_indent( self.block_mode[-2] )
            yield from self.fuzz_token( Shape.Symbol('}') )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def begin_line(self):
        if self.block_mode[-1]["type"] == "oneline":
            pass
        elif self.block_mode[-1]["type"] == "toplevel":
            pass
        elif self.block_mode[-1]["type"] == "indent":
            yield from self.fuzz_token( Shape.Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( Shape.Newline() )
            yield from self.fuzz_indent( self.block_mode[-1] )
        else:
            raise Exception("bad block mode", self.block_mode[-1])

    def end_line(self):
        if self.block_mode[-1]["type"] == "oneline":
            yield from self.fuzz_token( Shape.Symbol(';') )
            yield from self.fuzz_token( Shape.Whitespace(1) )
        elif self.block_mode[-1]["type"] == "toplevel":
            yield from self.fuzz_token( Shape.Newline() )
        elif self.block_mode[-1]["type"] == "indent":
            yield from self.fuzz_token( Shape.Newline() )
        elif self.block_mode[-1]["type"] == "nice_bracket":
            yield from self.fuzz_token( Shape.Newline() )
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