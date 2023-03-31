
from ...common import *

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

class Configurable(object):
    def __init__(self):
        self.config = ColliderConfig()
