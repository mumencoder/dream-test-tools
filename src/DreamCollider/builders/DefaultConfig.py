
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
        self.choose_option = choose_option
### Global
    	# total # of object blocks that will be added to AST 
        self.config.attr.object_block_count = max(1, round( random.gauss(12, 6))) 

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
        self.config.attr.obj.extend_path_prob = 0.25

        self.config.attr.obj.choices.op_extend.leaf = 8
        self.config.attr.obj.choices.op_extend.upwards = 1
        self.config.attr.obj.choices.op_extend.downwards = 1

        self.config.attr.obj.choices.path_prefix.absolute = 1
        self.config.attr.obj.choices.path_prefix.upwards = 4
        self.config.attr.obj.choices.path_prefix.downwards = 4
        self.config.attr.obj.choices.path_prefix.relative = 8
    	# which stdlib types can show up as an object block
        self.config.attr.obj.allowed_stdlib_types = list( self.stdlib.objects.keys() )
        generate_choices('.obj')

### Defines/Variables
        self.config.attr.define.var.empty_initializer_prob = 0.05
        self.config.attr.define.var.count = max(0, random.gauss(10, 5))
        def var_declare_remaining(self, env):
            return self.config.attr.define.var.count - len(self.toplevel.vars)
        type(self).var_declare_remaining = var_declare_remaining

### Defines/Procs
        self.config.attr.define.proc.count = max(0, random.gauss(10, 5) )
        self.config.attr.define.proc.is_verb_prob = 0.05
        self.config.attr.define.proc.arg.has_path_prob = 0.10
        self.config.attr.define.proc.arg.has_default_prob = 0.10
        self.config.attr.define.proc.arg.has_astype_prob = 0.10
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
        # "expr << expr"
        self.config.attr.define.proc.stmt.weights.type.output_irregular = 1
        generate_choices('.define.proc.stmt')

### Exprs
        self.config.attr.expr.param.is_named = 0.1