
import os, sys, asyncio, json, io, time, pathlib, yaml, collections, random, shutil, requests, gzip

import mumenrepo as Shared

def base_setup(env, output_dir):
    env = env.branch()
    env.attr.dirs.output = Shared.Path( output_dir )

    env.attr.shell.env = os.environ
    env.attr.process.stdout = sys.stdout
    env.attr.dirs.tmp = env.attr.dirs.output / 'tmp'

def setup_installs(env):
    benv = env.branch()
    benv.attr.version.major = 514
    benv.attr.version.minor = 1589
    benv.attr.install.dir =  env.attr.dirs.output / 'byond' / 'main'

    oenv = env.branch()
    oenv.attr.install.dir =  env.attr.dirs.output / 'opendream' / 'main'

    clenv = env.branch()
    clenv.attr.install.dir = env.attr.dirs.output / 'clopendream' / 'main'
    sys.path.append( str( clenv.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0') )

    env.attr.envs.byond = benv
    env.attr.envs.opendream = oenv
    env.attr.envs.clopendream = clenv

    return env

def load_config():
    if os.path.exists('server_config.yaml'):
        with open( 'server_config.yaml', "r") as f:
            config = yaml.load( f, yaml.Loader )
        for path_id, path in config["paths"].items():
            config["paths"][path_id] = Shared.Path( path )
    else:
        raise Exception("cannot read config")
    return config

import DMTestRunner as DMTR
import DMShared, DreamCollider as DreamCollider