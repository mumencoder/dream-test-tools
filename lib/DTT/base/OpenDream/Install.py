
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
        install.dir = env.attr.opendream.dirs.installs / install.id
        env.attr.install = install
        
    @staticmethod
    def from_github(env):
        _id = f"github.{env.attr.github.owner}.{env.attr.github.repo}.{env.attr.git.repo.commit}.{env.attr.github.tag}"
        Install.load(env, _id)
        env.attr.git.repo.local_dir = env.attr.install.dir
