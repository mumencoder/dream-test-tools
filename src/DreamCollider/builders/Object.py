
from ..common import *
from ..model import *

class RandomObjects(object):
    def choose_object(self, env):
        if len(self.toplevel.object_blocks) == 0:
            return None
        return random.choice( self.toplevel.object_blocks ) 

    def random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path
    
