
import collections 

class Tree(object):
    def __init__(self):
        self.branches = {}
        self.segment = None

    def get_branch(self, path):
        trunk = self
        for segment in path:
            if segment not in trunk.branches:
                trunk = Tree()
                trunk.segment = segment
                trunk.branches[segment] = trunk
            else:
                trunk = trunk.branches[segment]
        return trunk

    def dfs_visit_all(self):
        yield self
        for branch in self.branches.values():
            yield from branch.dfs_visit_all()

class InfiniteDefaultDict(object):
    def __init__(self):
        self.d = {}

    def __getitem__(self, k):
        if k not in self.d:
            self.d[k] = InfiniteDefaultDict()
        return self.d[k]

    def __setitem__(self, k, v):
        self.d[k] = v

    def __contains__(self, k):
        return k in self.d
        
    def get(self, k, default):
        if k not in self.d:
            return default
        return self.d[k]

    def items(self):
        return self.d.items()

    def initialize(idict, fdict):
        for k, v in fdict.items():
            if type(v) is dict:
                idict[k] = InfiniteDefaultDict()
                idict[k].initialize(v)
            else:
                idict[k] = v

    def finitize(idict):
        fdict = {}
        for k, v in idict.items():
            if type(v) is InfiniteDefaultDict:
                fdict[k] = v.finitize()
            else:
                fdict[k] = v
        return fdict
