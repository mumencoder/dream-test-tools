
from ...common import *
from ...model import *

class BlockDeclareAction(object):
    def __init__(self, start_block, object_tags):
        self.block_count = max(1, round( random.gauss(12, 6)) )
        self.current_blocks = set()
        self.declare_block_stack = [start_block]
        self.generate_block = self.default_block_generator
        self.object_tags = object_tags

    def finished(self, env):
        if self.block_count - len(self.current_blocks) <= 0:
            return True
        return False

    def __call__(self, env):
        parent_block = self.current_parent()
        new_block = self.generate_block(env)

        env.attr.builder.tags.add(new_block, *self.object_tags)
        self.current_blocks.add( new_block )
        self.declare_block_stack.append( new_block )
        pops = random.choice( [0,0,0,1,1,1,2,2,3] )
        while pops > 0 and len(self.declare_block_stack) > 1:
            self.declare_block_stack.pop()

        parent_block.add_leaf( new_block )

    def default_block_generator(self, env):
        new_block = env.attr.builder.initialize_node( AST.ObjectBlock() )
        new_block.path = env.attr.builder.generate_object_path(env)
        return new_block

    def current_parent(self):
        return self.declare_block_stack[-1]
        
class RandomObjects(object):
    def config_object_paths(self, config):
        config.set("obj.path.block_join_prob", 0.10)
        config.set("obj.path.extend_prob", 0.50)

    def generate_object_path(self, parent_block):
        extend_chance = self.config.prob( "obj.path.op_extend" )

        prefix_type = self.config.choose_option( "obj.path.prefix_type" )
        match prefix_type:
            case 'absolute':
                path = ["/"]
                extend = random.random() < 0.999
                state = "name"
            case 'upwards':
                path = ["."]
                extend = random.random() < 0.999
                state = "name"
            case 'downwards':
                path = [":"]
                extend = random.random() < 0.999
                state = "name"
            case 'relative':
                name = f'ty{str(random.choice(list(range(0, 5))))}'
                path = [name]
                extend = extend_chance
                extend_chance /= 2.0
                state = "op"

        while extend:
            if state == "op":
                op_type = self.config.choose_option( "obj.path.extend_type" )
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
        return AST.ObjectPath.new(segments=tuple(path))

    def generate_random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path