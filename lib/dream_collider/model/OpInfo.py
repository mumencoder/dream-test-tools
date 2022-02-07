
from . import *

class Op(object):
    def __init__(self, display, arity, fixity):
        self.display = display
        self.arity = arity
        self.fixity = fixity
        self.prec = None
        if len(self.arity) != self.fixity.count("_"):
            raise Exception("arity mismatch", self.display)

class OpInfo(object):
    def __init__(self):
        self.arity = None
        self.ops = {}

        self.create_ops()
        self.set_prec()

    def set_arity(self,*args):
        self.arity = args

    def op(self,name,fixity=None,display=None):
        if display is None:
            display = name
        if fixity is None and len(self.arity) == 2:
            fixity = ["_", name, "_"]
        self.ops[name] = Op(display, self.arity, fixity)
        return True

    def create_ops(b):
        b.set_arity("lval")
        b.op("pre++", fixity=["++", "_"], display="++")
        b.op("pre--", fixity=["--", "_"], display="--")
        b.op("post++", fixity=["_", "++"], display="++")
        b.op("post--", fixity=["_", "--"], display="--")

        b.set_arity("rval")
        b.op("!", fixity=["!", "_"])
        b.op("~", fixity=["~", "_"])
        b.op("()", fixity=["(", "_", ")"])

        b.set_arity("lval", "rval")
        b.op("=")
        b.op(":=")
        b.op("&=") and b.op("|=")
        b.op("^=") and b.op("||=") and b.op("&&=")
        b.op(">>=") and b.op("<<=")
        b.op("+=") and b.op("-=") and b.op("*=") and b.op("/=") and b.op("%=")

        b.set_arity("storage", "prop")
        b.op(".") and b.op("?.")
        b.op(":") and b.op("?:")

        b.set_arity("storage", "rval")
        b.op("[]", fixity=["_", "[", "_", "]"])
        b.op("?[]", fixity=["_", "?[", "_", "]"])

        b.set_arity("rval", "rval")
        b.op("&") and b.op("|") and b.op("^") 
        b.op("~=") and b.op("~!")
        b.op("&&") and b.op("||")
        b.op("<") and b.op(">") and b.op(">=") and b.op("<=") and b.op(">>") and b.op("<<") and b.op("<>")
        b.op("+") and b.op("-") and b.op("*") and b.op("/") and b.op("%")
        b.op("**") and b.op("==") and b.op("!=")

        b.set_arity("rval", "rval")
        b.op("in")

        b.set_arity("rval", "rval", "rval")
        b.op("?", fixity=["_", "?", "_", ":", "_"])

    def set_prec(b):
        def _set_prec(op, n):
            if op not in b.ops:
                return
            op = b.ops[op]
            op.prec = n
        for op in ["()"]:
            _set_prec(op, 360)
        for op in ["[]", ".", ":"]:
            _set_prec(op, 350)
        for op in ["in"]:
            _set_prec(op, 345)
        for op in ["?[]", "?.", "?:"]:
            _set_prec(op, 340)
        for op in ["~", "!", "-", "pre++", "post++", "pre--", "post--"]:
            _set_prec(op, 330)
        for op in ["**"]:
            _set_prec(op, 320)
        for op in ["*", "/", "%"]:
            _set_prec(op, 310)
        for op in ["+", "-"]:
            _set_prec(op, 300)
        for op in ["<", "<=", ">", ">="]:
            _set_prec(op, 290)
        for op in ["<<", ">>"]:
            _set_prec(op, 280)
        for op in ["==", "!=", "<>", "~=", "~!"]:
            _set_prec(op, 270)
        for op in ["&"]:
            _set_prec(op, 260)
        for op in ["^"]:
            _set_prec(op, 250)
        for op in ["|"]:
            _set_prec(op, 240)
        for op in ["&&"]:
            _set_prec(op, 230)
        for op in ["||"]:
            _set_prec(op, 220)
        for op in ["?"]:
            _set_prec(op, 210)
        # the -= operator is twice in doc!
        for op in ["=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", ":=", "&&=", "||="]:
            _set_prec(op, 200)