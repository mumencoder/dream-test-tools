
import os, sys, asyncio, json, io, time, pathlib, yaml, collections, random

import pythonnet
pythonnet.load("coreclr")
import clr

import mumenrepo as Shared
import DMShared, DMTestRunner, DreamCollider

import sys

def base_setup(env):
    env = env.branch()
    env.attr.dirs.output = Shared.Path( os.path.realpath( os.path.join( os.path.dirname(__file__), "..", "..", "output" )) )
    env.attr.shell.env = os.environ
    env.attr.process.stdout = sys.stdout
    env.attr.dirs.tmp = env.attr.dirs.output / 'tmp'

    benv = env.branch()
    benv.attr.version.major = 514
    benv.attr.version.minor = 1589
    benv.attr.install.dir =  env.attr.dirs.output / 'byond' / 'main'

    oenv = env.branch()
    oenv.attr.install.dir =  env.attr.dirs.output / 'opendream' / 'main'

    clenv = env.branch()
    clenv.attr.install.dir = env.attr.dirs.output / 'clopendream' / 'main'

    env.attr.envs.byond = benv
    env.attr.envs.opendream = oenv
    env.attr.envs.clopendream = clenv

    return env

def load_clopendream(env):
    sys.path.append( str( env.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net6.0') )
    clr.AddReference("ClopenDream")
    clr.AddReference("DMCompiler")

def load_opendream(env):
    sys.path.append( str( env.attr.install.dir / 'DMCompiler' / 'bin' / 'Release' / 'net6.0') )
    sys.path.append( str( env.attr.install.dir / 'bin' / 'Content.Server' ) )
    sys.path.append( str( env.attr.install.dir / 'bin' / 'Content.Tests' ) )
    clr.AddReference("DMCompiler")
    clr.AddReference("OpenDreamServer")
    clr.AddReference("OpenDreamRuntime")

def load_opendream_tests(env):
    clr.AddReference("Content.Tests")
    clr.AddReference("Robust.Shared")