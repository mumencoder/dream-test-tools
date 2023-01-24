from ..common import *

from .Errors import *
from ..Tree import *

class Semantics(object):
    class ObjectTree(object):
        class Node(object):
            def __init__(self):
                self.root = None
                self.path = tuple()
                self.trunk = None
                self.leaves = {}

                self.is_stdlib = False

            def iter_nodes(self):
                if len(self.path) > 0 and self.path[-1] == "proc":
                    return
                yield self
                for name, subnode in self.leaves.items():
                    yield from subnode.iter_nodes()
                
            def add_node(self, name):
                if name in self.leaves:
                    return self.leaves[name]
                node = Semantics.ObjectTree.Node()
                node.root = self.root
                node.trunk = self
                node.path = self.path + tuple([name])
                self.leaves[name] = node
                return node

            def leaf_search(self, name):
                if name not in self.leaves:
                    return None
                return self.leaves[name]

            def upwards_search(self, name):
                current_node = self
                while current_node is not None:
                    found_node = current_node.leaf_search( name )
                    if found_node is not None:
                        return found_node
                    else:
                        current_node = current_node.trunk
                return None

            def downwards_search(self, name):
                current_node = self
                found_node = current_node.leaf_search( name )
                if found_node is not None:
                    return found_node
                else:
                    for subnode in self.leaves.values():
                        found_node = subnode.downwards_search( name )
                        if found_node is not None:
                            return found_node 
                return None

        def __init__(self):
            self.root = Semantics.ObjectTree.Node()
            self.nodes_by_path = {}

        def iter_nodes(self):
            yield from self.root.iter_nodes()

        def add_node(self, trunk, name):
            node = trunk.add_node( name )
            self.nodes_by_path[node.path]( name )
            return node

        def add_path(self, path):
            current_node = self.root
            for name in path:
                current_node = current_node.add_node( name )
            return current_node

        def resolve(self, resolve_path, start_node=None, create_nodes=False):
            if type(resolve_path) is not AST.ObjectPath:
                raise Exception(resolve_path)

            if start_node is None:
                node = self.root
            else:
                node = start_node
            
            current_segment = 0
            def next_segment():
                nonlocal current_segment
                if current_segment >= len(resolve_path.segments):
                    return None
                segment = resolve_path.segments[current_segment]
                current_segment += 1
                return segment

            def resolve_name(name):
                if name[0] in ["/", ".", ":"]:
                    return name[1:]
                else:
                    return name

            segment = next_segment()
            state = None
            while segment != None:
                if segment not in [".",":","/"] and state == None:
                    state = "op"
                    name_segment = resolve_name(segment)
                    found_node = node.leaf_search( name_segment )
                elif segment in ['.',":","/"]:
                    name_segment = next_segment()
                    if name_segment in ['.',':','/']:
                        raise Exception("expected path name got ", name_segment)
                    match segment:
                        case ".":
                            found_node = node.upwards_search( name_segment )
                        case ":":
                            found_node = node.downwards_search( name_segment )
                        case "/":
                            found_node = node.leaf_search( name_segment )
                else:
                    raise Exception("unexpected segment", segment, state)
                if found_node is None:
                    if create_nodes:
                        node = node.add_node( name_segment )
                    else:
                        raise Exception("node is none", segment)
                else:
                    node = found_node
                segment = next_segment()

            return node

    class Toplevel:
        def init_semantics(self):
            self.tree = Semantics.ObjectTree()

            # local indices
            # TODO: these need to be ordered by tree position
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
                self.note_object_block( None, leaf )
            elif type(leaf) is AST.ObjectVarDefine:
                self.global_vars_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.ProcDefine:
                self.global_procs_by_name[leaf.name].append( leaf )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.root = self
            leaf.parent = None
            self.leaves.append( leaf )
            leaf.assign_block( self )

        def add_branch(self, branch):
            if len(branch) == 0:
                return
            node = branch[-1]
            self.add_leaf( node )
            branch.pop()
            node.add_branch( list(branch) )
   
        def note_object_block(self, trunk, leaf):
            if trunk is None:
                current_node = self.tree.resolve( leaf.path, create_nodes=True)
                leaf.resolved_path = current_node.path
            else:
                trunk_node = self.tree.resolve( trunk.path, create_nodes=True )
                current_node = self.tree.resolve( leaf.path, start_node=trunk_node, create_nodes=True)
                leaf.resolved_path = current_node.path

            self.object_blocks.append( leaf ) 
            self.object_blocks_by_path[leaf.path].append( leaf )

        def note_var(self, trunk, leaf):
            self.vars.append( leaf )
        
        def note_proc(self, trunk, leaf):
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
            self.resolved_path = None

            # TODO: these need to be ordered by tree position
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
            leaf.root = self.root
            leaf.parent = self
            self.leaves.append( leaf )
            if type(leaf) is AST.ObjectBlock:
                self.root.note_object_block( self, leaf )
            elif type(leaf) is AST.ObjectVarDefine:
                self.object_vars_by_name[leaf.name].append( leaf )
            elif type(leaf) is AST.ProcDefine:
                self.object_procs_by_name[leaf.name].append( leaf )
            else:
                raise Exception("invalid leaf", leaf)
            leaf.assign_block( self )

        def add_branch(self, branch):
            if len(branch) == 0:
                return
            node = branch[-1]
            self.add_leaf( node )
            branch.pop()
            node.add_branch( list(branch) )

        def assign_block(self, block):
            self.block = block

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
                    uses = self.object_vars_by_name[self.path]
                    if len(uses) == 0:
                        raise UsageError(self, use, 'UNDEF_VAR')
                    return uses[0]
                else:
                    if self.parent is not None:
                        return self.parent.resolve_usage(use)
                    else:
                        return self.root.resolve_usage(use)
            elif type(use) is AST.Expr.GlobalIdentifier:
                return self.root.resolve_usage(use)
            else:
                raise UsageError(self, use, 'INTERNAL')

    class ObjectVarDefine:
        def init_semantics(self):
            pass

        def get_storage_id(self):
            if self.is_global:
                return f"gvd@{self.name}"
            else:
                return f"ovd@{self.block.path}@{self.name}"

        def assign_block(self, block):
            self.block = block
            if type(self.block) is AST.Toplevel:
                self.is_global = True
                self.block.note_var( self )
            else:
                self.is_global = False
                self.block.root.note_var( self )

        def initialization_mode(self):
            #TODO: if override, inherits mode of overriden
            if self.is_global:
                if "const" in self.var_path:
                    return "const"
                return "dynamic"
            else:
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
                self.block.add_dependency( self, usage )
                if self.block.check_usage_cycle( self, usage ) is True:
                    self.errors.append( GeneralError('USAGE_CYCLE') )
    class ProcDefine:
        def init_semantics(self):
            pass

        def assign_block(self, block):
            self.block = block
            if type(self.block) is AST.Toplevel:
                self.is_global = True
                self.block.note_proc( self, block)
            else:
                self.is_global = False
                self.block.root.note_proc( self, block )

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