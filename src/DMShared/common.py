
import os, sys, asyncio, pathlib, time, shutil, json, random, re, gzip, textwrap, tarfile, pickle
import collections, io
import xml.dom.minidom as minidom

import mumenrepo as Shared

def load_dotnet(env):
    import pythonnet
    pythonnet.load("coreclr")
    import clr
    sys.path.append( str( env.attr.install.dir / 'DMCompiler' / 'bin' / 'Release' / 'net7.0') )
    sys.path.append( str( env.attr.install.dir / 'bin' / 'Content.Server' ) )
    sys.path.append( str( env.attr.install.dir / 'bin' / 'Content.Tests' ) )
    clr.AddReference("ClopenDream")
    clr.AddReference("DMCompiler")
    clr.AddReference("OpenDreamServer")
    clr.AddReference("OpenDreamRuntime")

def load_opendream_tests(env):
    clr.AddReference("Content.Tests")
    clr.AddReference("Robust.Shared")

def pipe_stdout(env):
    env.attr.process.stdout = io.StringIO()
    env.attr.process.stderr = env.attr.process.stdout
    env.attr.process.piped = True      

def pickle_env(env, names):
    d = []
    for name in names:
        if not env.attr_exists(name):
            raise Exception("missing env name", name)
        d.append( (name, env.get_attr(name)) )
    return pickle.dumps(d)

def unpickle_env(env, p):
    d = pickle.loads(p)
    for name, value in d:
        env.set_attr(name, value)