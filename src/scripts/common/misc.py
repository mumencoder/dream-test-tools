
from .imports import *

class Counter(object):
    def __init__(self):
        self.c = 0
        self.visible_states = [2 ** x for x in range(0,11)]
        self.visible = False

    def inc(self, n=1):
        self.c += n
        self.update_state()
        
    def update_state(self):
        if self.c in self.visible_states or self.c % self.visible_states[-1] == 0:
            self.visible = True
        else:
            self.visible = False

    def state(self):
        return self.visible

def get_file(filename, default_value=None):
    if not os.path.exists(filename):
        return default_value
    with open(filename, "rb") as f:
        return f.read()

def put_file(filename, data):
    with open(filename, "wb") as f:
        f.write(data)

def maybe_from_pickle(data, default_value=None):
    try:
        return pickle.loads(data)
    except:
        return default_value

def parse_csv(l):
    return [ s.strip() for s in l.split(',') if s.strip() != "," ]