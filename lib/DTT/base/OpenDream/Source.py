
import asyncio

import os
import pathlib

import Shared

class Source(object):
    @staticmethod
    def load(env, _id):
        source = env.prefix('.opendream.source')
        source.id = _id
        source.platform = 'opendream'
        source.dir = env.attr.opendream.dirs.sources / source.id
        env.attr.source = source