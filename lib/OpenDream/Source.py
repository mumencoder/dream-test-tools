
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

    @staticmethod
    def from_github(env, suffix_id):
        Source.load(env, f'{env.attr.github.repo_id}.{suffix_id}')
        env.attr.git.repo.local_dir = env.attr.source.dir
        env.attr.git.repo.url = env.attr.github.url