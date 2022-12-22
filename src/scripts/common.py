
import os, sys, asyncio, json, io, time, pathlib, yaml, collections, random, shutil

import mumenrepo as Shared
from startup import base_setup

baseenv = base_setup( Shared.Environment(), sys.argv[2] )
sys.path.append( str( baseenv.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0') )

def copy_dmstandard():
    src = baseenv.attr.envs.clopendream.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'DMStandard'
    dst = baseenv.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'DMStandard'
    if not os.path.exists( dst ):
        shutil.copytree(src , dst)

    src = baseenv.attr.envs.clopendream.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
    dst = baseenv.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
    if not os.path.exists( dst ):
        shutil.copy(src , dst)

copy_dmstandard()

import DMTestRunner as DMTR
import DMShared, DreamCollider

import sys

