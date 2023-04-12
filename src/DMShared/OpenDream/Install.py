
from ..common import *

from . import Builder

class Install(object):
    @staticmethod
    def load_repo(env, data):
        env.attr.git.repo.url = data.url
        env.attr.git.repo.dir = data.path

    def load_install_from_repo(env):
        env.attr.install.dir = env.attr.git.repo.dir

