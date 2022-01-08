
class ProcVarDecl(object):
    def __init__(self):
        self.var_type = None
        self.var_name = None
        self.flags = []
        self.initial = None

    def __str__(self):
        path = "var/"
        for flag in self.flags:
            path += flag + '/'
        path += self.var_name
        return path + ' = ' + str(self.initial)

class ReturnStatement(object):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "return " + str(self.expr)