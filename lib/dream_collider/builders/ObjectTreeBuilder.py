
from ..model import *

import Shared

class ObjectTreeBuilder(object):
    def __init__(self):
        self.possible_paths = []
        self.def_len = 1

        self.should_compile = True
        self.notes = []

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
        while True:
            ty = Shared.Random.choose_choices( config['otree_builder.statement.type'], 1 )[0]

            if ty == "var":
                decl = ObjectVarDecl()
                decl.path = self.path(config)
                decl.flags = self.flags(config)
                decl.name = self.var_name(config)
                result = config['model'].can_add_decl(config, decl)
                if result["valid"] is False:
                    continue
                else:
                    self.should_compile = self.should_compile and result["should_compile"]
                    self.notes += result["notes"]
                return decl
            elif ty == "proc":
                decl = ProcDecl()
                decl.path = self.path(config)
                decl.name = self.proc_name(config)
                result = config['model'].can_add_decl(config, decl)
                if result["valid"] is False:
                    continue
                else:
                    self.should_compile = self.should_compile and result["should_compile"]
                    self.notes += result["notes"]
                return decl
            else:
                raise Exception("invalid choice of statement type")
