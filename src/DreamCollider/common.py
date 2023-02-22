
import asyncio, time, shutil, os, json, random, io, math, sys, itertools
import string
import collections

import mumenrepo as Shared

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

class ColliderConfig(object):
    def __init__(self):
        self.param_declares = set()
        self.params = {}
        self.choices = {}

    def declare_param(self, name):
        self.param_declares.add( name )

    def set(self, name, value):
        self.params[name] = value

    def get(self, name):
        return self.params[name]

    def prob(self, name):
        return random.random() < self.params[name]

    def set_choice(self, name, **kvs):
        self.choices[name] = kvs

    def choose_option(self, name):
        return random.choices( list(self.choices[name].keys()), list(self.choices[name].values()) )[0]