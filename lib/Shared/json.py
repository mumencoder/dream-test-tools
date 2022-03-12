
import pathlib
import json

class Json(object):
    class BetterEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, pathlib.PurePath):
                return str(obj)
            return json.JSONEncoder.default(self, obj)