
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