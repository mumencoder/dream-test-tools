
import re
import random
import types

class Prefix(object):
    def __init__(self, root, path):
        object.__setattr__(self, 'root', root)
        object.__setattr__(self, 'path', path)

    def __getattribute__(self, attr):
        cnode = object.__getattribute__(self, 'root')
        path = object.__getattribute__(self,'path') + "." + attr
        while path not in cnode.properties:
            cnode = cnode.parent
            if cnode is None:
                return Prefix(object.__getattribute__(self, 'root'), path)
        return cnode.properties[path]

    def __hasattribute__(self, attr):
        cnode = object.__getattribute__(self, 'root')
        path = object.__getattribute__(self,'path') + "." + attr
        while path not in cnode.properties:
            cnode = cnode.parent
            if cnode is None:
                return False
        return True

    def __setattr__(self, attr, value):
        cnode = object.__getattribute__(self, 'root')
        path = object.__getattribute__(self, 'path') + "." + attr
        cnode.properties[path] = value

    def __delattr__(self, attr):
        cnode = object.__getattribute__(self, 'root')
        path = object.__getattribute__(self, 'path') + "." + attr
        del cnode.properties[path]

    def __repr__(self):
        return f"<PREFIX {object.__getattribute__(self,'path')}>"

class Environment(object):
    def __init__(self, parent=None):
        self.properties = {}
        self.branches = {}
        self.event_handlers = {}
        self.parent = parent
        self.name = ""
        self.attr = Prefix(self, "")

    def parent_chain(self):
        cnode = self
        while cnode is not None:
            yield cnode
            cnode = cnode.parent

    def event_defined(self, event_name):
        for cnode in self.parent_chain():
            if event_name in cnode.event_handlers:
                return True
        return False

    async def send_event(self, event_name, *args, **kwargs):
        for cnode in self.parent_chain():
            if event_name in cnode.event_handlers:
                await cnode.event_handlers[event_name](*args, **kwargs)
            
    def get_dict(self, path):
        d = {}
        for cnode in self.parent_chain():
            if path not in cnode.properties:
                continue
            if type(cnode.properties[path]) is not dict:
                continue
            d.update(cnode.properties[path])
        return d

    def prefix(self, path):
        return Prefix(self, path)

    def get_list(self, value):
        l = []
        for cnode in self.parent_chain():
            if value not in cnode.properties:
                continue
            l.append(cnode[value])
        return l

    def copy(self):
        nnode = Config()
        for node in reversed(list(self.parent_chain())):
            nnode.properties.update( node.properties )
            nnode.event_handlers.update( node.event_handlers )
        return nnode

    def fullname(self):
        if self.parent is not None:
            return self.parent.fullname() + "/" + self.name 
        else:
            return self.name

    def root(self):
        while self.parent is not None:
            self = self.parent
        return self

    def parse_path(self, path):
        node = ""
        for c in path:
            if c == "/" or c == "." or c == ":":
                if node != "":
                    yield node
                    node = ""
                yield c
            else:
                node += c
        if node != "":
            yield node

    def all_branches(self):
        yield self
        for branch in self.branches.values():
            yield from branch.all_branches()

    def unique_properties(self):
        seen = set()
        for env in self.parent_chain():
            for prop in env.properties:
                if prop in seen:
                    continue
                seen.add(prop)
                yield prop

    def filter_properties(self, re_filter):
        re_filter = re_filter.replace(".", "\.")
        re_filter = re_filter.replace("*", ".*")
        pattern = re.compile(re_filter)
        for prop in self.unique_properties():
            if pattern.fullmatch(prop):
                yield prop

    def set_attr(self, path, value):
        self.properties[path] = value

    def get_attr(self, path, local=False, default=None):
        if local is True:
            return self.properties[path]
        while path not in self.properties:
            self = self.parent
            if self is None:
                return default
        return self.properties[path]

    def attr_exists(self, path, local=False):
        if local is True:
            return path in self.properties
        while path not in self.properties:
            self = self.parent
            if self is None:
                return False
        return True

    def get(self, path, default=None):
        if self.attr_exists(path):
            return self.get_attr(path)
        else:
            return default

    def upwards(self, name):
        while self.name != name:
            if self.parent is None:
                return None
            self = self.parent
        return self

    def downwards(self, name):
        for key, branch in self.branches.items():
            if key == name:
                return self.branches[name]
            
    def branch_segment(self, segment):
        if segment not in self.branches:
            self.branches[segment] = Environment(parent=self)
            self.branches[segment].name = segment
        return self.branches[segment]

    def merge(self, config, inplace=False):
        if inplace:
            new_env = self
        else:
            new_env = self.branch()
        for parent in reversed(list(config.parent_chain())):
            new_env.properties.update(parent.properties)
            new_env.event_handlers.update(parent.event_handlers)
        return new_env

    def branch(self, path=None):
        if path is None:
            path = ''.join(random.choice("012345679") for i in range(12))
        if path in self.branches:
            raise Exception("branch exists", path)
        here = self
        path_segments = list(self.parse_path(path))
        if path_segments[0] == "/":
            here = self.root()
            path_segments = path_segments[1:]
        i = 0
        while i < len(path_segments):
            segment = path_segments[i]
            if segment == ".":
                here = here.upwards(path_segments[i+1])
                i += 2
            elif segment == ":":
                here = here.downwards(path_segments[i+1])
                i += 2
            elif segment == "/":
                here = here.branch_segment(path_segments[i+1])
                i += 2
            else:
                here = here.branch_segment(segment)
                i += 1
        return here

    def pop(self):
        return self.parent
