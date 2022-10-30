
import sys, os, io, time, asyncio, pathlib
import pymongo, yaml

sys.path.append( os.path.join( os.path.dirname(__file__),"..","..") )

import Shared, DMShared
from dream_collider import *

def load_config(env):
    with open(os.environ["COLLIDER_CONFIG"]) as f:
        env.attr.collider.config = yaml.safe_load(f)

def load_dotnet(env):
    import pythonnet
    pythonnet.load("coreclr")
    import clr

    config = env.attr.collider.config
    sys.path.append( str( Shared.Path( config["opendream"]["repo_dir"] ) / 'DMCompiler' / 'bin' / 'Debug' / 'net6.0') )
    sys.path.append( str( Shared.Path( config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Server' ) )
    sys.path.append( str( Shared.Path( config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Tests' ) )
    clr.AddReference("DMCompiler")
    clr.AddReference("OpenDreamServer")
    clr.AddReference("OpenDreamRuntime")
    clr.AddReference("Content.Tests")
    clr.AddReference("Robust.Shared")