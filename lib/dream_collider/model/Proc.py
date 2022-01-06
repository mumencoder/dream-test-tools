
import random 

from ..model import *

class ProcArgument(object):
    def __init__(self, name, type_path, flags=[]):
        self.name = name
        self.type_path = type_path
        self.flags = flags

    def __str__(self):
        display = str(self.type_path) + "/"
        for flag in self.flags:
            display += flag + "/"
        display += self.name
        return display
        
class ProcDecl(object):
    def __init__(self):
        self.path = None
        self.name = None
        self.stdlib = False
        self.allow_override = True
        self.args = []
        self.statements = []

    def __str__(self):
        if self.stdlib:
            return ""
        if len(self.path.segments) != 0:
            path = str(self.path) + '/'
        else:
            path = "/"
        if not self.is_override:
            path += f'proc/'
        path += f'{self.name}'
        display = path + "("
        has_arg = False
        display += ",".join([str(arg) for arg in self.args])
        display += ")\n"
        for statement in self.statements:
            display += '  ' + str(statement) + '\n'
        return display

    def has_prev_decl(self, decl):
        if decl == self: 
            return True
        elif self.prev_decl is None:
            return False
        else:
            return self.prev_decl.has_prev_decl( decl )

    def usage(self, config):
        return CallExpression(self.name)
