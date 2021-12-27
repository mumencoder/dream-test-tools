
class Path(object):
    def __init__(self, segments):
        self.segments = tuple(segments)
        self.str = str(self)

    def parent_paths(self):
        cpath = []
        for segment in self.segments:
            cpath.append(segment)
            yield Path(cpath)

    def contains(self, path):
        for i, segment in enumerate(path.segments):
            if i >= len(self.segments):
                return False
            if segment != self.segments[i]:
                return False
        return True

    def __eq__(self, o):
        return self.segments == o.segments

    def __hash__(self):
        return hash(self.segments)

    def from_string(path):
        return Path( [seg for seg in path.split("/") if seg != ""] )

    def __str__(self):
        return "/" + "/".join(self.segments)
