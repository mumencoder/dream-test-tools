
from ...common import *
from ...model import *

class RandomObjects(object):
    def choose_object(self, env):
        if len(self.toplevel.object_blocks) == 0:
            return None
        return random.choice( self.toplevel.object_blocks ) 

    def config_object(self, config):
        def object_declare_remaining(self, env):
            return config.attr.object_block_count - len(self.toplevel.object_blocks)
        type(self).object_declare_remaining = object_declare_remaining

    	# total # of object blocks that will be added to AST 
        config.attr.object_block_count = max(1, round( random.gauss(12, 6))) 

        # probability that a single-leaf declare will be joined with its parent
        config.attr.path_join_prob = 0.5

        # probability that an user object proc/var declaration will be syntactically an override
        config.attr.override_user_define_prob = 0.5

        # probability that a stdlib object proc/var declaration will be syntactically an override
        config.attr.override_stdlib_define_prob = 0.5

        config.attr.obj.extend_path_prob = 0.25

    def config_object_paths(self, config):
        config.attr.obj.choices.op_extend.leaf = 8
        config.attr.obj.choices.op_extend.upwards = 1
        config.attr.obj.choices.op_extend.downwards = 1

        config.attr.obj.choices.path_prefix.absolute = 1
        config.attr.obj.choices.path_prefix.upwards = 4
        config.attr.obj.choices.path_prefix.downwards = 4
        config.attr.obj.choices.path_prefix.relative = 8
        # which stdlib types can show up as an object block
        config.attr.obj.allowed_stdlib_types = list( self.stdlib.objects.keys() )

    def generate_object_path(self, parent_block):
        prefix_type = self.choose_option( self.config.attr.obj.choices.path_prefix )
        extend_chance = self.config.attr.obj.extend_path_prob

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
                extend = random.random() < extend_chance
                extend_chance /= 2.0
                state = "op"

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
        return AST.ObjectPath.new(segments=tuple(path))

    def declare_object(self, env):
        parent_block = self.declare_block_stack[-1]
        new_block = self.initialize_node( AST.ObjectBlock() )

        new_block.path = self.generate_object_path(parent_block)
        parent_block.add_leaf( new_block )
        self.declare_block_stack.append( new_block )

    def generate_random_path(self):
        path = self.initialize_node( AST.Expr.Path() )
        path.prefix = random.choice( ['.', '/', ':'] )
        path.types = [ random.choice( ['ty1', 'ty2', 'ty3'] ) ]
        path.ops = []
        for i in range(0, random.randint(0, 2)):
            path.ops.append( random.choice( ['.', '/', ':'] ) )
            path.types.append( path.types[i] + random.choice( ['1', '2', '3'] ) )
        return path
    
