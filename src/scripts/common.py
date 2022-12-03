
import os, sys, asyncio, json, io, time, pathlib, yaml, collections, random

import pythonnet
pythonnet.load("coreclr")
import clr

import mumenrepo as Shared
import DMShared, DMTestRunner, DreamCollider

import sys

def base_setup():
    env = Shared.Environment()
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

async def compile_byond(tenv):
    cenv = tenv.branch()

    cenv.attr.process.stdout = open(tenv.attr.test.path / 'byond.compile.stdout.txt', "w")
    await DMShared.Byond.Compilation.compile(cenv)
    with open(tenv.attr.test.path / 'byond.compile.stdout.txt', "r") as f:
        cenv.attr.compilation.log = f.read()

    with open(tenv.attr.test.path / "byond.compile.returncode.txt", "w") as f:
        f.write( str(cenv.attr.compilation.returncode) )
    cenv.attr.process.stdout.close()

    return cenv

async def run_byond(tenv, cenv):
    renv = None
    if cenv.attr.compilation.returncode == 0:
        renv = tenv.branch()
        renv.attr.run.exit_condition = DMShared.Byond.Run.wait_test_output
        renv.event_handlers['process.wait'] = DMShared.Byond.Run.wait_run_complete
        renv.attr.process.stdout = open(renv.attr.test.path / 'byond.run.stdout.txt', "w")
        renv.attr.run.dm_file_path = DMShared.Byond.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        renv.attr.run.args = {'trusted':True}
        await DMShared.Byond.Run.run(renv)
        renv.attr.process.stdout.close()
        with open(renv.attr.test.path / 'byond.run.stdout.txt', "r") as f:
            renv.attr.run.log = f.read()
        if os.path.exists( renv.attr.test.path / 'test.out.json'):
            with open( renv.attr.test.path / 'test.out.json', "r" ) as f:
                try:
                    renv.attr.run.output = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            os.remove( renv.attr.test.path / 'test.out.json')

    return renv