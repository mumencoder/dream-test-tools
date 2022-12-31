
from ..common import *
from ..model import *

class RandomObjects(object):
    def choose_object(self, env):
        if len(self.toplevel.object_blocks) == 0:
            return None
        return random.choice( self.toplevel.object_blocks ) 

    def declare_object(self, env, current_block):
        new_block = self.initialize_node( AST.ObjectBlock() )
        if type(current_block) is AST.Toplevel:
            new_block.name = random.choice( ['ty1', 'ty2', 'ty3'])
        else:
            new_block.name = current_block.name + random.choice( ['1', '2', '3'])
        return new_block

    def object_declare_count(self, env):
        return 4 - len(self.toplevel.object_blocks)

    def random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path
    
