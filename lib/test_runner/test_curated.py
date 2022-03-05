
import os

import Shared

class Curated(object):
    @staticmethod
    def load_test(env):
        relpath = os.path.relpath(env.attr.test.source_file.parent, env.attr.tests.dirs.root)
        if relpath == ".":
            groups = ["curation"]
        else:
            groups = ["curation"] + relpath.split("/")

        groups += [env.attr.test.source_file.with_suffix("").name]
        env.attr.test.id = "-".join(groups) 
        env.attr.test.root_dir = env.attr.tests.dirs.output / env.attr.test.id
        env.attr.test.base_dir = env.attr.test.root_dir / f'{env.attr.install.platform}.{env.attr.install.id}'

    @staticmethod
    def prepare_test(env):
        with open(env.attr.test.source_file, "r") as f:
            env.attr.test.text = f.read() + '\n'

