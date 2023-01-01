
from ..common import *

from ..Tree import *

class DefaultConfig:

    def initialize_config(self):
        self.config = Shared.Environment()

        def generate_choices(pattern):
            filter_pattern = pattern + '.*'
            choice_dict = collections.defaultdict(lambda: collections.defaultdict(list))
            for prop in self.config.filter_properties(filter_pattern):
                names = prop.split(".")
                option = names[-1]
                wclass = names[-2]
                weight = self.config.get_attr(prop)
                choice_dict[wclass]["options"].append(option)
                choice_dict[wclass]["weights"].append(weight)

            for wclass, results in choice_dict.items():
                self.config.set_attr(f"{pattern}.choices.{wclass}", results)

        def choose_option(wclass):
            return random.choices( wclass["options"], wclass["weights"] )[0]
        type(self).choose_option = choose_option
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
        self.config.attr.obj.weights.type.user = 7
    	# weight that object block will belong to a new type
        self.config.attr.obj.weights.type.new_user = 2
    	# weight that object block will belong to a stdlib type
        self.config.attr.obj.weights.type.stdlib = 1
    	# which stdlib types can show up as an object block
        self.config.attr.obj.allowed_stdlib_types = list( self.stdlib.objects.keys() )

        generate_choices('.obj')

        def declare_object(self, env):
            declare_type = choose_option( self.config.attr.obj.choices.type )

            if declare_type == "new_user":
                if len( self.user_object_blocks ) == 0:
                    parent_block = self.toplevel
                else:
                    parent_block = random.choice( [self.toplevel] + self.user_object_blocks )
                block = self.initialize_node( AST.ObjectBlock() )
                block.name = f'ty{str( random.choice( list(range(0, 5)) ) )}'
                block.define_mode = "user"
                self.user_object_blocks.append( block )
                self.finalize_node( parent_block, block )
                parent_block.add_leaf( block )
            elif declare_type == "user":
                if len( self.user_object_blocks ) == 0:
                    return
                copy_block = random.choice( self.user_object_blocks )
                copy_path = []
                while copy_block is not None:
                    copy_path.append( copy_block )
                    copy_block = copy_block.parent
                ast_block = self.toplevel
                for copy_block in copy_path:
                    block = self.initialize_node( AST.ObjectBlock() )
                    block.name = copy_block.name
                    block.define_mode = "user"
                    self.user_object_blocks.append( block )
                    self.finalize_node( ast_block, block )
                    ast_block.add_leaf( block )
                    ast_block = block
            elif declare_type == "stdlib":
                stdlib_path = random.choice( self.config.attr.obj.allowed_stdlib_types )
                copy_path = []
                ast_block = self.toplevel
                for path in reversed(stdlib_path):
                    block = self.initialize_node( AST.ObjectBlock() )
                    block.name = path
                    block.define_mode = "stdlib"
                    self.stdlib_object_blocks.append( block )
                    self.finalize_node( ast_block, block )
                    ast_block.add_leaf( block )
                    ast_block = block
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

### Defines/Procs/Stmts
        # "world << expr"
        self.config.attr.define.proc.stmt.weights.type.output_normal = 5
        # expr << expr
        self.config.attr.define.proc.stmt.weights.type.irregular_weight = 1