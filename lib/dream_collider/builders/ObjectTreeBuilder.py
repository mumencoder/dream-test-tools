
from ..model import *

import Shared

class ObjectTreeBuilder(object):
    def __init__(self):
        self.possible_paths = []
        self.def_len = 1

    def add_path(self, path):
        if type(path) is str:
            self.possible_paths.append( Path.from_string(path) )
        elif type(path) is Path:
            self.possible_paths.append( path )

    def defaults(self, config):
        config['otree_builder.statement.type'] = Shared.Random.to_choices( {"var":0.8, "proc":0.2} )
        config['otree_builder.flags.static'] = 0.05
        config['otree_builder.flags.const'] = 0.05
        config['otree_builder.flags.tmp'] = 0.05

    def var_name(self, config):
        name = None
        while name in [None, "as", "if", "in", "UP", "do", "to"]:
            name = Shared.Random.generate_string(self.def_len)
        return name

    def proc_name(self, config):
        name = None
        while name in [None, "as", "if", "in", "UP", "do", "to"]:
            name = Shared.Random.generate_string(self.def_len)
        return name

    def path(self, config):
        return random.choice(self.possible_paths)

    def flags(self, config):
        flags = []

        a = random.random()
        if a < config['otree_builder.flags.static']:
            flags.append("static")
        a = random.random()
        if a < config['otree_builder.flags.const']:
            flags.append("const")
        a = random.random()
        if a < config['otree_builder.flags.tmp']:
            flags.append("tmp")
        return flags

    def decl(self, config):
        ty = Shared.Random.choose_choices( config['otree_builder.statement.type'], 1 )[0]

        if ty == "var":
            decl = ObjectVarDecl()
            decl.path = self.path(config)
            decl.flags = self.flags(config)

            config['model'].scope = decl.path
            while True:
                decl.name = self.var_name(config)
                if config['model'].ident_in_scope(decl.name) is True:
                    continue
                break

        elif ty == "proc":
            decl = ProcDecl()
            decl.path = self.path(config)

            config['model'].scope = decl.path
            while True:
                decl.name = self.proc_name(config)
                if config['model'].ident_in_scope(decl.name) is True:
                    continue
                break
        else:
            raise Exception("invalid choice of statement type")

        return decl