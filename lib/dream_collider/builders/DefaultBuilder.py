
import random, string
import Shared

from ..model import *
from ..common import *

class DefaultBuilder(object):
    @staticmethod
    def identifier(config):
        return "".join([random.choice(string.ascii_lowercase) for i in range(0,n)])

    @staticmethod
    def const_int(config):
        return ConstExpression(random.randint(-100,100))

    @staticmethod
    def const_float(config):
        return ConstExpression(random.randint(-100,100) + random.randint(0,10000) / 10000)

    @staticmethod
    def const_string(config):
        return ConstExpression(random.choice(['"a"', '"b"', '"c"']))

    def log_statements(self, decl):
        if decl.path == "/":
            CallExpression(Identifier("LOG"), String(f"{decl.path}-{decl.name}"), Identifier(decl.name))