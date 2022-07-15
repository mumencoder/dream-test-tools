
import asyncio

import os
import pathlib

import Shared

class Install(object):
    @staticmethod
    def load(env, _id):
        install = env.prefix('.opendream.install')
        install.id = _id
        install.platform = 'opendream'
        install.tag = f'{install.platform}.{install.id}'
        env.attr.install = install