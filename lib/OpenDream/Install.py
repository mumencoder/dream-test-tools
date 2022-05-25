
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
        install.dir = env.attr.opendream.dirs.installs / install.id
        env.attr.install = install
        
    @staticmethod
    def from_github(env, suffix, commit=None):
        if commit is None:
            commit = env.attr.git.repo.remote_ref
        _id = f"{env.attr.github.owner}.{env.attr.github.repo}.{commit}.{suffix}"
        Install.load(env, _id)