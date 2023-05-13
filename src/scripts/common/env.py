
from .imports import *

class EnvTracker(object):
    def __init__(self, env, title, update_existing=True):
        self.env = env
        self.title = title
        self.seen = set()
        if update_existing:
            self.update()

    def update(self):
        self.seen = set()
        for prop in self.env.unique_properties():
            self.seen.add(prop)

    def print_local(self):
        print(f"=== {self.title} local")
        for prop in self.env.local_properties():
            print(prop, type(self.env.get_attr(prop)))

    def print(self, count): 
        print(f"=== {self.title} {count}")
        for prop in self.env.unique_properties():
            if prop in self.seen:
                continue
            print(prop, type(self.env.get_attr(prop)))
        for seen in self.seen:
            if not self.env.has_attr(seen):
                print(f"{prop} - removed")
        self.update()

def env_tod(env, d, props=None):
    if props is None:
        props = env.unique_properties()
    for prop in props:
        d[prop] = env.get_attr(prop)
    return d

def env_fromd(env, d):
    for k, v in d.items():
        env.set_attr(k, v)
    return env

import DreamCollider