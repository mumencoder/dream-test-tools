
class Blank(object):
    class Toplevel(object): pass
    class ObjectBlock(object): pass
    class VarDefine(object): pass
    #class ObjectMultiVarDefine(object): pass
    class ProcDefine(object): pass
    class ProcArgument(object): pass
    class Stmt(object):
        class Expression(object): pass
        class ObjectVarDefine(object): pass
        #class MultiVarDefine(object): pass
        class Return(object): pass
        class Break(object): pass
        class Continue(object): pass
        class Goto(object): pass
        class Label(object): pass
        class Del(object): pass
        class Set(object): pass
        class Spawn(object): pass
        class If(object): pass
        class For(object): pass
        class ForEnumerator(object): pass
        class While(object): pass
        class DoWhile(object): pass
        class Switch(object):
            class Case(object): pass
        class Try(object):
            class Catch(object): pass
        class Throw(object): pass

    class Expr(object):
        class Identifier(object): pass
        class GlobalIdentifier(object): pass
        class Integer(object): pass
        class Float(object): pass
        class String(object): pass
        class FormatString(object): pass
        class Resource(object): pass
        class Null(object): pass
        class Path(object): pass
        class List(object): 
            class Param(object): pass
        class Call(object):
            class Param(object): pass
            class Identifier(object):pass
            class Expr(object): pass
        class Super(object): pass
        class Self(object): pass
        class Input(object): pass
        class ModifiedType(object): pass
        class Pick(object): pass
        class New(object): pass