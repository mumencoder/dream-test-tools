
import asyncio, time, shutil, os, json, random, io, math, sys, itertools
import string
import collections

from .ColliderConfig import *

import mumenrepo as Shared

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