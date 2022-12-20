
import os, sys, json, textwrap, collections

import mumenrepo as Shared
import DMShared

def get_file(tenv, path):
    if tenv.attr_exists(f'.test.metadata.paths.{path}'):
        with open( tenv.attr.test.root_dir / getattr(tenv.attr.test.metadata.paths, path), "r") as f:
            setattr( tenv.attr.test.files, path, f.read() )

def new_file_from_path(tenv, path, filename):
    setattr( tenv.attr.test.metadata.paths, path, filename )
    get_file( tenv, path )
