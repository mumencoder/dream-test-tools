
import pathlib

class Json(object):
    def json_purepath(obj):
        if isinstance(obj, pathlib.PurePath):
            return str(obj)
        else:
            raise TypeError()