
from ..common import *
from ..model import *

class RandomObjects(object):
    def choose_object(self, env):
        if len(self.toplevel.object_blocks) == 0:
            return None
        return random.choice( self.toplevel.object_blocks ) 

    def declare_object_path(self, parent_block):
        path = []
        extend_chance = self.config.attr.obj.extend_path_prob
        extend = True
        state = random.choice( ["op", "name"] )
        while extend:
            if state == "op":
                op_type = self.choose_option( self.config.attr.obj.choices.op_extend )
                match op_type:
                    case 'leaf':
                        path.append( '/' )
                    case 'upwards':
                        path.append( '.' )
                    case 'downwards':
                        path.append( ':' )
                state = "name"
                extend = True
            if state == "name":
                name = f'ty{str(random.choice(list(range(0, 5))))}'
                path.append( name )
                state = "op"
                extend = random.random() < extend_chance
                extend_chance /= 2.0
        return self.create_objectpath( tuple(path) )

    def create_objectpath(self, segments):
        node = AST.ObjectPath()
        node.segments = segments
        return node

    def declare_object(self, env):
        parent_block = self.declare_block_stack[-1]
        new_block = self.initialize_node( AST.ObjectBlock() )

        new_block.path = self.declare_object_path(parent_block)

        self.finalize_node( parent_block, new_block )
        parent_block.add_leaf( new_block )
        self.declare_block_stack.append( new_block )

    def random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path
    
