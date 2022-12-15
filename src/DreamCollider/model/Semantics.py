
from ..common import *

from .dmast import *

class UsageError(Exception):
    def __init__(self, scope, node, error_code):
        self.scope = scope
        self.node = node
        self.error_code = error_code

class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UsageError):
            return obj.error_code
        return json.JSONEncoder.default(self, obj)

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
            self.object_blocks_by_path = collections.defaultdict(list)

            self.decl_deps = collections.defaultdict(set)
            self.decl_cycles = collections.defaultdict(set)
          
        def collect_errors(self, acc_errs):
            for node in AST.walk_subtree(self):
                for error in node.errors:
                    acc_errs.append( (node.lineno, error) )
            print(acc_errs)
            return acc_errs

        def get_vars(self):
            return list(self.global_vars_by_name.values())

        def iter_blocks(self):
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
            for block in self.iter_blocks():
                for var in block.iter_vars():
                    yield var

        def iter_proc_defines(self):
            for block in self.iter_blocks():
                for proc in block.iter_procs():
                    yield proc

        def add_leaf(self, leaf):
            if type(leaf) is AST.ObjectBlock:
                self.object_blocks_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.GlobalVarDefine:
                self.global_vars_by_name[leaf.name].append( leaf )
                leaf.assign_block( self )
            elif type(leaf) is AST.GlobalProcDefine:
                self.global_procs_by_name[leaf.name].append( leaf )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self
            leaf.parent = None
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.note_object_block( leaf )
    
        def note_object_block(self, leaf):
            self.object_blocks_by_path[leaf.path].append( leaf )

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
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self.root
            leaf.parent = self
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                leaf.compute_path()
                self.root.note_object_block( leaf )

        def compute_path(self):
            path = []
            cnode = self
            while cnode is not None:
                path.append(cnode.name)
                cnode = cnode.parent
            self.path = AST.Path( list(reversed(path)) )

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

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if "const" in self.var_path:
                return "const"

            return "dynamic"

        def set_expression(self, expr):
            self.expression = expr
            usages = expr.get_usage(self.block)
            for usage in usages:
                self.block.root.add_dependency( self, usage )
                if self.block.root.check_usage_cycle( self, usage ) is True:
                    self.expr_errors.append( "usage cycle ")

    class ObjectVarDefine:
        def init_semantics(self):
            self.allow_override = True

        def get_storage_id(self):
            return f"ovd@{self.block.path}@{self.name}"

        def assign_block(self, block):
            self.block = block

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if "static" in self.var_path:
                return "dynamic"
            else:
                return "const"

        def set_expression(self, expr):
            self.expression = expr
            usages = expr.get_usage(self.block)
            for usage in usages:
                self.block.root.add_dependency( self, usage )
                if self.block.root.check_usage_cycle( self, usage ) is True:
                    self.expr_errors.append( "usage cycle ")

    class GlobalProcDefine:
        def init_semantics(self):
            self.allow_override = True
            self.allow_verb = True

        def set_params(self, params):
            self.params = params

        def set_body(self, body):
            self.body = body

    class ObjectProcDefine:
        def init_semantics(self):
            self.allow_override = True
            self.allow_verb = True

        def set_params(self, params):
            self.params = params

        def set_body(self, body):
            self.body = body

    class Expr:
        class Identifier:
            def get_usage( self, scope ):
                try:
                    usage = scope.resolve_usage( self )
                except UsageError as e:
                    self.errors.append( e )
                    return []
                return usage

    def initialize():
        for ast_ty, sem_ty in Shared.Type.mix_types(AST, Semantics):
            if sem_ty in [Semantics, Semantics.Expr]:
                continue
            for p in dir(sem_ty):
                if p.startswith("__"):
                    continue
                setattr(ast_ty, p, getattr(sem_ty, p))

        for ast_ty, sem_ty in Shared.Type.mix_types(AST, Dependency):
            if sem_ty in [Dependency]:
                continue
            for p in dir(sem_ty):
                if p.startswith("__"):
                    continue
                setattr(ast_ty, p, getattr(sem_ty, p))

        def no_usage(self, scope):
            return []

        def expr_usage(self, scope):
            usages = []
            for expr in self.exprs:
                usages += expr.get_usage(scope)
            return usages

        for ty in Shared.Type.iter_types(AST.Op):
            if ty in [AST.Expr, AST.Op]:
                continue
            if not hasattr(ty, 'get_usage'):
                ty.get_usage = expr_usage

        for ty in Shared.Type.iter_types(AST):
            if ty in [AST, AST.Op, AST.Expr]:
                continue
            if not hasattr(ty, 'get_usage'):
                ty.get_usage = no_usage

class Dependency(object):
    class Toplevel(object):
        def check_usage_cycle(self, define_user, define_usee):
            if define_user.get_storage_id() == define_usee.get_storage_id(): 
                return True

            checking = set([define_usee.get_storage_id()])
            checked = set()

            while len(checking) > 0:
                for defn in checking:
                    if defn not in checked:
                        next_check = defn
                        break
                if define_user.get_storage_id() == next_check:
                    return True

                for defn in self.decl_deps[next_check]:
                    if defn in checked:
                        continue
                    checking.add(defn)
                checked.add(next_check)
                checking.remove(next_check)
            return False

        def add_dependency(self, define_user, define_usee):
            if self.check_usage_cycle(define_user, define_usee):
                self.decl_cycles.add( (define_user, define_usee) )
            self.decl_deps[define_user.get_storage_id()].add( define_usee.get_storage_id() )

Semantics.initialize()