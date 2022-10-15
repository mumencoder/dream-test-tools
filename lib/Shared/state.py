
import os
import Shared

class StateHandle(object):
    def __init__(self, state_cls, name):
        self.state_cls = state_cls
        self.name = name

    def get(self, default=None):
        return self.state_cls.get(self.name, default=default)

    def set(self, value):
        return self.state_cls.set(self.name, value)

class State(object):
    def __init__(self):
        pass

    @staticmethod
    def open(env, **keys):
        if env.attr_exists('.state.context', local=True):
            raise Exception("State context already assigned")
        else:
            env.attr.state.context = keys
            env.attr.state.prefix = env.get_dict('.state.context')

    def __call__(self, env, value=None, **kwargs):
        if value is not None:
            kwargs["value"] = value
        name = ""
        if len(kwargs) == 0:
            raise Exception("no key for state object")
        kwargs.update( env.attr.state.prefix )
        for key in sorted(kwargs.keys()):
            name += f"{key}={kwargs[key]}."
        return StateHandle(self, name)

class FilesystemState(State):
    def __init__(self, path, mode="", loader=lambda o: o, saver=lambda o: o):
        self.path = path
        self.mode = mode

        self.loader = loader
        self.saver = saver

    def get(self, key, default=None):
        if not os.path.exists(self.path / key):
            return default
        
        with Shared.File.open(self.path / key, "r" + self.mode) as f:
            result = f.read()
            if len(result) == 0:
                return default
                
        return self.loader( result )

    def set(self, key, value):
        with Shared.File.open(self.path / key, "w" + self.mode) as f:
            f.write( self.saver(value) )

    def rm(self, key):
        try:
            os.remove( self.path / key )
        except OSError:
            pass

    def reset(self, key):
        if not os.path.exists(self.path / key):
            return
        else:
            os.remove( self.path / key )