
from ..common import *

from ..Tree import *

class DefaultConfig:
    def initialize_config(self):
        self.config = Shared.Environment()
### Global
    	# total # of object blocks that will be added to AST 
        self.config.attr.object_block_count = max(0, random.gauss(10, 5))

        def object_declare_remaining(self, env):
            return self.config.attr.object_block_count - len(self.toplevel.object_blocks)
        type(self).object_declare_remaining = object_declare_remaining

        # probability that a single-leaf declare will be joined with its parent
        self.config.attr.path_join_prob = 0.5

        # probability that an user object proc/var declaration will be syntactically an override
        self.config.attr.override_user_define_prob = 0.5

        # probability that a stdlib object proc/var declaration will be syntactically an override
        self.config.attr.override_stdlib_define_prob = 0.5

### Object Blocks

    	# weight that object block will belong to an existing user type
        self.config.attr.obj.user_type_weight = 7
    	# weight that object block will belong to a new type
        self.config.attr.obj.new_user_type_weight = 2
    	# weight that object block will belong to a stdlib type
        self.config.attr.obj.stdlib_type_weight = 1
    	# which stdlib types can show up as an object block
        self.config.attr.obj.allowed_stdlib_types = list( self.stdlib.objects.keys() )

        def declare_object(self, env):
            options = ["user_type", "new_user_type", "stdlib_type"]
            weights = [self.config.attr.obj.user_type_weight, self.config.attr.obj.new_user_type_weight, self.config.attr.obj.stdlib_type_weight]
            declare_type = random.choices( options, weights )[0]

            if declare_type == "new_user_type":
                if len( self.user_object_blocks ) == 0:
                    parent_block = self.toplevel
                else:
                    parent_block = random.choice( [self.toplevel] + self.user_object_blocks )
                block = self.initialize_node( AST.ObjectBlock() )
                block.name = f'ty{str( random.choice( list(range(0, 5)) ) )}'
                parent_block.add_leaf( block )
                self.user_object_blocks.append( block )
            elif declare_type == "user_type":
                if len( self.user_object_blocks ) == 0:
                    return
                new_branch = []
                copy_block = random.choice( self.user_object_blocks )
                while copy_block is not None:
                    block = self.initialize_node( AST.ObjectBlock() )
                    block.name = copy_block.name
                    new_branch.append( block )
                    self.user_object_blocks.append( block )
                    copy_block = copy_block.parent
                self.toplevel.add_branch( new_branch )
            elif declare_type == "stdlib_type":
                new_branch = []
                stdlib_path = random.choice( self.config.attr.obj.allowed_stdlib_types )
                for path in reversed(stdlib_path):
                    block = self.initialize_node( AST.ObjectBlock() )
                    block.name = path
                    self.stdlib_object_blocks.append( block )
                    new_branch.append( block )
                self.toplevel.add_branch( new_branch )
            else:
                raise Exception("unknown block selection")

        type(self).declare_object = declare_object

### Defines/Variables
        self.config.attr.define.var.empty_initializer_prob = 0.05
        self.config.attr.define.var.count = max(0, random.gauss(10, 5))
        def var_declare_remaining(self, env):
            return self.config.attr.define.var.count - len(self.toplevel.vars)
        type(self).var_declare_remaining = var_declare_remaining

### Defines/Procs
        self.config.attr.define.proc.is_verb_prob = 0.05
        self.config.attr.define.proc.count = max(0, random.gauss(5, 2.5) )
        def determine_proc_stmt_count(self, env):
            return max(0, random.gauss(6, 3))
        type(self).determine_proc_stmt_count = determine_proc_stmt_count
        def determine_proc_arg_count(self, env):
            return max(0, random.gauss(3, 1.5))
        type(self).determine_proc_arg_count = determine_proc_arg_count
        def proc_declare_remaining(self, env):
            return self.config.attr.define.proc.count - len(self.toplevel.procs)
        type(self).proc_declare_remaining = proc_declare_remaining
