
from .common import *

import pythonnet
pythonnet.load("coreclr")
import clr

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