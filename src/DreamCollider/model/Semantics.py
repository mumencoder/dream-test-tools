from ..common import *

from .Errors import *
from ..Tree import *

class Semantics(object):
    class Toplevel:
        def init_semantics(self):
            # local indices
            # TODO: these need to be ordered by tree position
            self.object_blocks_by_name = collections.defaultdict(list)
            self.global_vars_by_name = collections.defaultdict(list)
            self.global_procs_by_name = collections.defaultdict(list)

            # toplevel indices
            # TODO: these need to be ordered by tree position
            self.object_blocks = [self]
            self.vars = []
            self.procs = []

            self.object_blocks_by_path = collections.defaultdict(list)

            self.decl_deps = collections.defaultdict(set)
            self.decl_cycles = set()
          
        ### Accessors
        def get_vars(self):
            return list(self.global_vars_by_name.values())

        def iter_objects(self):
            yield self
            for leaf_list in list(self.object_blocks_by_name.values()):
                for leaf in leaf_list:
                    yield leaf

        def iter_vars(self):
            for var_list in list(self.global_vars_by_name.values()):
                for var in var_list:
                    yield var

        def iter_procs(self):
            for proc_list in list(self.global_procs_by_name.values()):
                for proc in proc_list:
                    yield proc

        def iter_var_defines(self):
            for block in self.iter_objects():
                for var in block.iter_vars():
                    yield var

        def iter_proc_defines(self):
            for block in self.iter_objects():
                for proc in block.iter_procs():
                    yield proc

        ### Builders
        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.GlobalVarDefine:
                self.global_vars_by_name[leaf.name].append( leaf )
                leaf.assign_block( self )
            elif type(leaf) is AST.GlobalProcDefine:
                self.global_procs_by_name[leaf.name].append( leaf )
                leaf.assign_block( self )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self
            leaf.parent = None
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.note_object_block( leaf )

        def add_branch(self, branch):
            if len(branch) == 0:
                return
            node = branch[-1]
            self.add_leaf( node )
            branch.pop()
            node.add_branch( list(branch) )
   
        def note_object_block(self, leaf):
            self.object_blocks.append( leaf ) 
            self.object_blocks_by_path[leaf.path].append( leaf )

        def note_var(self, leaf):
            self.vars.append( leaf )
        
        def note_proc(self, leaf):
            self.procs.append( leaf )

        ### Errors
        def collect_errors(self, acc_errs):
            for node in AST.walk_subtree(self):
                for error in node.errors:
                    acc_errs.append( (node.lineno, error) )
            return acc_errs

        ### Semantics
        def resolve_usage(self, use):
            if type(use) is AST.Expr.Identifier:
                if len( self.global_vars_by_name[ use.name ] ) == 0:
                    raise UsageError(self, use, 'UNDEF_VAR')
                return self.global_vars_by_name[ use.name ][0]
            elif type(use) is AST.Expr.GlobalIdentifier:
                if len( self.global_vars_by_name[ use.name ] ) == 0:
                    raise UsageError(self, use, 'UNDEF_VAR')
                return self.global_vars_by_name[ use.name ][0]
            else:
                raise UsageError(self, use, 'INTERNAL')

    class ObjectBlock:
        def init_semantics(self):
            self.root = None
            self.parent = None

            # TODO: these need to be ordered by tree position
            self.object_blocks_by_name = collections.defaultdict(list)
            self.object_vars_by_name = collections.defaultdict(list)
            self.object_procs_by_name = collections.defaultdict(list)

        # TODO: compare set() performance
        def dfs_compare(nodel, noder):
            lpath = []
            cnode = nodel
            while cnode is not None:
                lpath.append(cnode)
                cnode = cnode.parent
            cnode = noder
            while cnode is not None and cnode not in lpath:
                cnode = cnode.parent
            if cnode is None:
                block = nodel.root
            else:
                block = cnode
            #TODO

        def iter_vars(self):
            for var_list in self.object_vars_by_name.values():
                for var in var_list:
                    yield var

        def iter_procs(self):
            for proc_list in self.object_procs_by_name.values():
                for proc in proc_list:
                    yield proc

        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.ObjectVarDefine:
                self.object_vars_by_name[leaf.name].append( leaf )
                leaf.assign_block(self)
            elif type(leaf) is AST.ObjectProcDefine:
                self.object_procs_by_name[leaf.name].append( leaf )
                leaf.assign_block( self )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self.root
            leaf.parent = self
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.root.note_object_block( leaf )

        def add_branch(self, branch):
            if len(branch) == 0:
                return
            node = branch[-1]
            self.add_leaf( node )
            branch.pop()
            node.add_branch( list(branch) )

        def compute_path(self):
            path = []
            cnode = self
            while cnode is not None:
                path.append(cnode.name)
                cnode = cnode.parent
            self.path = Semantics.Path( list(reversed(path)) )

        # TODO: support parent_type assignment
        def parent_chain(self, include_self=True, include_root=True):
            if include_self:
                cnode = self
            else:
                cnode = self.parent
            while cnode is not None:
                yield cnode
                cnode = cnode.parent
            if include_root:
                yield self.root

        def resolve_usage(self, use):
            if type(use) is AST.Expr.Identifier:
                if use.name in self.object_vars_by_name:
                    return self.object_vars_by_name[self.path][0]
                else:
                    if self.parent is not None:
                        return self.parent.resolve_usage(use)
                    else:
                        return self.root.resolve_usage(use)
            elif type(use) is AST.Expr.GlobalIdentifier:
                return self.root.resolve_usage(use)
            else:
                raise UsageError(self, use, 'INTERNAL')

    class GlobalVarDefine:
        def init_semantics(self):
            self.allow_override = True

        def get_storage_id(self):
            return f"gvd@{self.name}"

        def assign_block(self, block):
            self.block = block
            self.block.note_var( self )

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if "const" in self.var_path:
                return "const"
            return "dynamic"

        def set_expression(self, expr):
            self.expression = expr
            expr.validate()
            usages = expr.get_usage(self.block)
            if not expr.is_const(self) and self.initialization_mode() == "const":
                self.errors.append( ConstError(self, expr, 'EXPECTED_CONSTEXPR') )
            for usage in usages:
                self.block.add_dependency( self, usage )
                if self.block.check_usage_cycle( self, usage ) is True:
                    self.errors.append( GeneralError('USAGE_CYCLE') )

    class ObjectVarDefine:
        def init_semantics(self):
            self.allow_override = True

        def get_storage_id(self):
            return f"ovd@{self.block.path}@{self.name}"

        def assign_block(self, block):
            self.block = block
            self.block.root.note_var( self )

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if "static" in self.var_path:
                return "dynamic"
            else:
                return "const"

        def set_expression(self, expr):
            self.expression = expr
            expr.validate()
            usages = expr.get_usage(self.block)
            if not expr.is_const(self) and self.initialization_mode() == "const":
                self.errors.append( ConstError(self, expr, 'EXPECTED_CONSTEXPR') )
            for usage in usages:
                self.block.root.add_dependency( self, usage )
                if self.block.root.check_usage_cycle( self, usage ) is True:
                    self.expr_errors.append( GeneralError('USAGE_CYCLE') )

    class GlobalProcDefine:
        def init_semantics(self):
            self.allow_override = True
            self.allow_verb = True

        def assign_block(self, block):
            self.block = block
            self.block.note_proc( self )

        def add_param(self, param):
            self.params.append( param )

        def add_stmt(self, stmt):
            self.body.append( stmt )

    class ObjectProcDefine:
        def init_semantics(self):
            self.allow_override = True
            self.allow_verb = True

        def assign_block(self, block):
            self.block = block
            self.block.root.note_proc( self )

        def add_param(self, param):
            self.params.append( param )

        def add_stmt(self, stmt):
            self.body.append( stmt )

    class Path(object):
        def __init__(self, segments):
            self.segments = tuple(segments)

        def parent_paths(self):
            cpath = []
            for segment in self.segments:
                cpath.append(segment)
                yield Semantics.Path(cpath)

        def contains(self, path):
            for i, segment in enumerate(path.segments):
                if i >= len(self.segments):
                    return False
                if segment != self.segments[i]:
                    return False
            return True

        def __str__(self):
            return str(self.segments)

        def __eq__(self, o):
            return self.segments == o.segments

        def __hash__(self):
            return hash(self.segments)

        def from_string(path):
            return Semantics.Path( [seg for seg in path.split("/") if seg != ""] )

    def initialize():
        ### Semantics setup
        for ast_ty, sem_ty in Shared.Type.mix_types(AST, Semantics):
            if sem_ty in [Semantics]:
                continue
            for p in dir(sem_ty):
                if p.startswith("__"):
                    continue
                setattr(ast_ty, p, getattr(sem_ty, p))

        ### Dependency Setup
        from .Dependency import Dependency
        for ast_ty, sem_ty in Shared.Type.mix_types(AST, Dependency):
            if sem_ty in [Dependency]:
                continue
            for p in dir(sem_ty):
                if p.startswith("__"):
                    continue
                setattr(ast_ty, p, getattr(sem_ty, p))

        ### Usage setup
        from .Usage import Usage
        for ast_ty, sem_ty in Shared.Type.mix_types(AST, Usage):
            if sem_ty in [Usage, Usage.Expr]:
                continue
            for p in dir(sem_ty):
                if p.startswith("__"):
                    continue
                setattr(ast_ty, p, getattr(sem_ty, p))

        for ty in Shared.Type.iter_types(AST.Op):
            if ty in [AST, AST.Op]:
                continue
            if not hasattr(ty, 'get_usage'):
                ty.get_usage = Usage.op_usage

        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            if not hasattr(ty, 'get_usage'):
                ty.get_usage = Usage.no_usage

        ### Const setup
        from .Const import Const
        for ty in Shared.Type.iter_types(AST.Expr):
            ty.is_const = Const.never_const

        for ty in Shared.Type.iter_types(AST.Op):
            ty.is_const = Const.subtree_const
            
        for ty in [AST.Expr.Integer, AST.Expr.Float]:
            ty.is_const = Const.always_const

        for ty_name in ["LessThan", "LessEqualThan", "GreaterThan", "GreaterEqualThan", 
            "Equals", "NotEquals", "NotEquals2", "Equivalent", "NotEquivalent"]:
            ty = getattr(AST.Op, ty_name)
            ty.is_const = Const.never_const

        AST.Op.To.is_const = Const.never_const
        AST.Op.In.is_const = Const.never_const 

        ### Validate setup
        from .Validate import Validate 
        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            if not hasattr(ty, 'validate'):
                ty.validate = Validate.subtree_valid

        for ast_ty, sem_ty in Shared.Type.mix_types(AST, Validate):
            if sem_ty in [Validate, Validate.Expr, Validate.Op]:
                continue
            for p in dir(sem_ty):
                if p.startswith("__"):
                    continue
                setattr(ast_ty, p, getattr(sem_ty, p))

    @staticmethod
    def init_semantics(node):
        node.errors = []

class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SemanticError):
            return obj.error_code
        return json.JSONEncoder.default(self, obj)

Semantics.initialize()