
import os, sys, asyncio, pathlib, time, shutil, json, random, re, gzip, textwrap, tarfile, pickle, requests, psutil
from bs4 import BeautifulSoup
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