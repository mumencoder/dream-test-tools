
from ..common import *
from ..model import *

class RandomBlocks(object):
    def blocks_remaining(self, env):
        if not env.attr_exists('.gen.blocks_left'):
            env.attr.gen.blocks_left = random.randint(1, 8)
        return env.attr.gen.blocks_left

    def get_block(self, env, phase=None):
        return random.choice( list(self.toplevel.iter_blocks()) )

    def create_block(self, env, current_block):
        new_block = self.initialize_node( AST.ObjectBlock() )
        if type(current_block) is AST.Toplevel:
            new_block.name = random.choice( ['ty1', 'ty2', 'ty3'])
        else:
            new_block.name = current_block.name + random.choice( ['1', '2', '3'])
        return new_block

    def random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path
    
