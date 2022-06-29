
from .common import *

class Install(object):
    def config(env):
        env.attr.resources.compile = Shared.CountedResource(1)
        env.attr.resources.run = Shared.CountedResource(1)
