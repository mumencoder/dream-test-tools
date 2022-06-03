
import os

import Shared

class Install(object):
    @staticmethod
    async def load(env):
        info = env.attr.ss13.install.info
        if info["type"] == "repo":
            env.attr.ss13.base_dir  = env.attr.ss13.dirs.installs / env.attr.ss13.install.id
            env.attr.git.local_dir = env.attr.ss13.base_dir
            await Shared.Git.Repo.prepare(env, info)
        else:
            raise Exception("unknown install type")

    @staticmethod
    def is_dme(name):
        return name.split('.')[-1] == 'dme'

    @staticmethod
    def find_dme(env):
        base_dir = env.attr.ss13.base_dir
        if not os.path.exists(base_dir):
            raise Exception("DME directory does not exist")
            
        dme_list = [entry for entry in os.listdir(base_dir) if Install.is_dme(entry)]
        if len(dme_list) == 1:
            env.attr.ss13.dme_file = base_dir / dme_list[0]
        else:
            env.attr.ss13.dme_file = None
