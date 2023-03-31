
from ...common import *

def safe_choice(l):
    if len(l) == 0:
        return None
    else:
        return random.choice(l)

def keyword_object_block(path):
    return 'proc' in path or 'verb' in path or 'var' in path

class Tags(object):
    def __init__(self):
        self.tags = collections.defaultdict(list)

    def add(self, obj, *tags):
        for tag in tags:
            self.tags[tag].append( obj )

class Action(object):
    def finished(action, env):
        return action.total_count <= action.current_count
    
    def counted(action, count):
        action.total_count = count
        action.current_count = 0
        action.finished = lambda env: Action.finished(action, env)