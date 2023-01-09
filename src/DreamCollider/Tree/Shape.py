
from .dmast import *

class Shape(object):
    def Line():
        return {"type":"Line"}
    def BeginNode(node):
        return {"type":"BeginNode", "node":node}
    def EndNode(node):
        return {"type":"EndNode", "node":node}

    def Keyword(text):
        return {"type":"Keyword", "text":text}
    def Symbol(text):
        return {"type":"Symbol", "text":text}
    def Text(text, type):
        return {"type":"Text", "text":text, "subtype":type}
    def BeginParen():
        return {"type":"BeginParen"}
    def EndParen():
        return {"type":"EndParen"}
    def Newline():
        return {"type":"Newline"}
    def Whitespace(n=0):
        return {"type":"Whitespace", "n":n}

    def BeginBlock():
        return {"type":"BeginBlock"}
    def EndBlock():
        return {"type":"EndBlock"}
    def BeginLine():
        return {"type":"BeginLine"}
    def EndLine():
        return {"type":"EndLine"}

    def Fuzz():
        return {"type":"Fuzz"}

    def marshall(tokens):
        result = []
        for token in tokens:
            if token["type"] == "BeginNode":
                result.append( {"type":"BeginNode", "node": id(token["node"])} )
            elif token["type"] == "EndNode":
                result.append( {"type":"EndNode", "node": id(token["node"])} )
            else:
                result.append( dict(token) )
        return result

    def unmarshall(tokens, ast):
        nodes = {}
        for node in AST.walk_subtree(ast):
            if node is None:
                continue
            nodes[ node.marshall_id ] = node
        for token in tokens:
            if token["type"] == "BeginNode":
                yield {"type":"BeginNode", "node": nodes[token["node"]]}
            elif token["type"] == "EndNode":
                yield {"type":"EndNode", "node": nodes[token["node"]]}
            else:
                yield dict(token)

    def token_lines(self, tokens):
        si = ShapeIter()
        self.reset_state()
        current_line = 1
        current_tokens = []
        for token in tokens:
            while current_line < self.current_line:
                yield current_tokens
                current_tokens = []
                current_line += 1
            current_tokens.append( token )
            self.update_state(token)

    def coalesce_newlines(self, tokens):
        newline = True
        for token in tokens:
            if token["type"] == "Newline":
                if newline is True:
                    pass
                else:
                    yield token
                newline = True
            elif token["type"] in ["Text", "Symbol", "Keyword", "Whitespace"]:
                newline = False
                yield token
            elif token["type"] in ["BeginNode", "EndNode", "Line"]:
                yield token
            else:
                raise Exception("unknown token", token)

    def strip_nonprintable(self, tokens):
        for token in tokens:
            if token["type"] in ["Text", "Symbol", "Keyword", "Newline"]:
                yield token
            else:
                pass

class ShapeIter(object):
    def __init__(self, tokens):
        self.current_line = 1
        self.node_lines = {}
        self.node_stack = []

        self.tokens = tokens

    def current_node(self):
        return self.node_stack[-1]

    def update_state(self, token):
        match token["type"]:
            case "BeginNode":
                self.node_stack.append( token["node"] )
            case "EndNode":
                self.node_stack.pop()
            case "Line":
                node = self.node_stack[-1]
                if not hasattr(node, 'lineno'):
                    self.node_lines[node] = self.current_line
            case "Newline":
                self.current_line += 1