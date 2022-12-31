
from ..common import *

from ..Tree import *

class DefaultConfig:
    def initialize_config(self):
        self.config = Shared.Environment()

    	# object blocks contained in the entire test
        self.config.attr.object_block_count = max(0, random.gauss(10, 5))

        def object_declare_count(self, env):
            return self.config.attr.object_block_count - len(self.toplevel.object_blocks)
        type(self).object_declare_count = object_declare_count

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
                    copy_block = copy_block.parent
                self.toplevel.add_branch( new_branch )
            elif declare_type == "stdlib_type":
                new_branch = []
                stdlib_path = random.choice( self.config.attr.obj.allowed_stdlib_types )
                for path in reversed(stdlib_path):
                    block = self.initialize_node( AST.ObjectBlock() )
                    block.name = path
                    new_branch.append( block )
                self.toplevel.add_branch( new_branch )
            else:
                raise Exception("unknown block selection")

        type(self).declare_object = declare_object

