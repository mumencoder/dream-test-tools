
from ..stdlib import init_all
from ..model import *

class StdlibBuilder(object):
    def __init__(self, toplevel):
        self.toplevel = toplevel
        init_all(self)

    def dmtype(self, path):
        self.toplevel.ensure_object( Path.from_string(path) )
        self.current_path = Path.from_string(path)

    def parent_type(self, path):
        self.toplevel.parent_type(Path.from_string(path), self.current_path)

    def dmproc(self, name, allow_override=True):
        decl = ProcDecl()
        decl.path = self.current_path
        decl.name = name
        decl.stdlib = True
        decl.allow_override = allow_override
        self.toplevel.add_decl( decl )

    def dmvar(self, name, allow_override=True):
        decl = ObjectVarDecl()
        decl.name = name
        decl.path = self.current_path
        decl.stdlib = True
        decl.allow_override = allow_override
        self.toplevel.add_decl( decl )

    def dmop(self, name):
        pass
