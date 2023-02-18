
from ...common import *
from ...model import *

class RandomObjectDeclareAction(object):
    def __init__(self, start_block, object_tags):
        self.current_blocks = set()
        self.declare_block_stack = [start_block]
        self.generate_object_path = None
        self.object_tags = object_tags

    def __call__(self, env):
        parent_block = self.current_parent()
        new_block = env.attr.builder.initialize_node( AST.ObjectBlock() )
        new_block.path = self.generate_object_path(env)

        env.attr.builder.tags.add(new_block, *self.object_tags)
        self.current_blocks.add( new_block )
        self.declare_block_stack.append( new_block )
        pops = random.choice( [0,0,0,1,1,1,2,2,3] )
        while pops > 0 and len(self.declare_block_stack) > 1:
            self.declare_block_stack.pop()

        parent_block.add_leaf( new_block )
        self.current_count += 1

    def current_parent(self):
        return self.declare_block_stack[-1]

class ToplevelDeclareAction(object):
    def __init__(self, toplevel):
        self.toplevel = toplevel
        self.choose_path = None

    def __call__(self, env):
        path = self.choose_path(env)
        prev_block = None
        top_block = None
        for segment in path:
            current_block = env.attr.builder.initialize_node( AST.ObjectBlock() )
            current_block.path = AST.ObjectPath.new(segments=tuple([segment]))
            if top_block is None:
                top_block = current_block
                self.toplevel.add_leaf( top_block )
            if prev_block is not None:
                prev_block.add_leaf( current_block )
            prev_block = current_block
        self.current_count += 1
        return top_block

def ChooseAnyObjectBlock(env, builder):
    choices = builder.toplevel.object_blocks
    return random.choice( choices )

class ObjectPathChooser(object):
    def __init__(self, path_choices):
        self.path_choices = list(path_choices)

    def __call__(self, env):
        return random.choice( self.path_choices )

class ObjectPathGenerator(object):
    def new_config(self):
        config = ColliderConfig()

        config.declare_param("obj.path.prefix_type")
        config.declare_param("obj.path.extend_path_prob")
        config.declare_param("obj.path.extend_type")

        return config

    def __init__(self, builder, config):
        self.builder = builder
        self.config = config

    def __call__(self, env):
        extend_chance = self.config.prob( "obj.path.extend_path_prob" )

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