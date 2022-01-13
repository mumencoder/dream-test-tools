
import types

class Config(object):
    def __init__(self, parent=None):
        self.properties = {}
        self.branches = {}
        self.event_handlers = {}
        self.parent = parent
        self.name = ""

    def parent_chain(self):
        cnode = self
        while cnode is not None:
            yield cnode
            cnode = cnode.parent

    async def send_event(self, event_name, *args, **kwargs):
        for cnode in self.parent_chain():
            if event_name in cnode.event_handlers:
                await cnode.event_handlers[event_name](*args, **kwargs)
            
    def get_dict(self, value):
        d = {}
        for cnode in self.parent_chain():
            if value not in cnode.properties:
                continue
            if type(cnode[value]) is not dict:
                continue
            d.update(cnode[value])
        return d

    def get_list(self, value):
        l = []
        for cnode in self.parent_chain():
            if value not in cnode.properties:
                continue
            l.append(cnode[value])
        return l

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

    def all_properties(self):
        for branch in self.all_branches():
            for p_name, p_value in branch.properties.items():
                yield branch, p_name, p_value

    def exists(self, value):
        while value not in self.properties:
            self = self.parent
            if self is None:
                return False
        return True

    def get(self, value, default=None):
        if self.exists(value):
            return self[value]
        else:
            return default

    def __getitem__(self, value):
        while value not in self.properties:
            self = self.parent
            if self is None:
                raise Exception(f"unable to locate {value}")
        return self.properties[value]

    def __setitem__(self, attr, value):
        self.properties[attr] = value

    def __delitem__(self, attr):
        del self.properties[attr]

    def __enter__(self):
        return self

    def __exit__(self, _1, _2, _3):
        return 

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
            self.branches[segment] = Config(parent=self)
            self.branches[segment].name = segment
        return self.branches[segment]

    def merge(self, config):
        new_config = self.branch("merge")
        new_config.properties.update(config.properties)
        new_config.event_handlers.update(config.event_handlers)
        return new_config

    def branch(self, path="branch"):
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
