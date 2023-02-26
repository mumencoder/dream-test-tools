
import os, sys, asyncio, json, io, time, re, pathlib, yaml, collections, random, shutil, gzip, threading

import requests 

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

import fastapi
import redis

import mumenrepo as Shared

### helpers
def print_env(env, title):
    print(f"=== {title}")
    for prop in env.unique_properties():
        print(prop, type(env.get_attr(prop)))

### config
def load_config(env):
    if os.path.exists('server_config.yaml'):
        with open( 'server_config.yaml', "r") as f:
            config = yaml.load( f, yaml.Loader )
        for path_id, path in config["paths"].items():
            config["paths"][path_id] = Shared.Path( path )
    else:
        raise Exception("cannot read config")
    env.attr.config = config
    env.attr.dirs.tmp = Shared.Path( env.attr.config["paths"]["tmp"] )

def setup_base(env):
    env.attr.shell.env = os.environ
    env.attr.process.stdout = sys.stdout

### ast generation
def generate_ast(env):
    env.attr.expr.depth = 3
    env.attr.ast.builder.build_all( env )

    env.attr.ast.fuzzer = DreamCollider.Fuzzer(env.attr.ast.builder.config)
    env.attr.ast.ast_tokens = list(env.attr.ast.fuzzer.fuzz_shape( env.attr.ast.builder.toplevel.shape() ) )
    env.attr.ast.ngram_info = DreamCollider.NGram.compute_info( env.attr.ast.ast_tokens )

# compilation
async def install_byond(benv):
    benv.attr.process.stdout = io.StringIO()
    benv.attr.process.stderr = benv.attr.process.stdout
    benv.attr.process.piped = True

    benv.attr.state.installed = False
    await DMShared.Byond.install(benv)
    benv.attr.state.installed = True

async def install_opendream(oenv):
    oenv.attr.process.stdout = io.StringIO()
    oenv.attr.process.stderr = oenv.attr.process.stdout
    oenv.attr.process.piped = True

    oenv.attr.state.installed = False
    await DMShared.OpenDream.Install.init_repo(oenv)
    await DMShared.OpenDream.Builder.build(oenv)
    oenv.attr.state.installed = True

async def byond_compilation(env):
    cenv = benv.branch()
    cenv.attr.compilation.root_dir = genv.attr.dirs.tmp / 'random_ast' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( env.attr.ast.text )
    await DMShared.Byond.Compilation.managed_compile(cenv)
    await DMShared.Byond.Compilation.managed_objtree(cenv)

    renv = env.branch()
    DMShared.Byond.Compilation.load_objtree(cenv, renv)
    DMShared.Byond.Compilation.load_compile(cenv, renv)
    return renv

async def opendream_compilation(env):
    cenv = oenv.branch()
    cenv.attr.compilation.root_dir = genv.attr.dirs.tmp / 'random_ast' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( env.attr.ast.text )
    await DMShared.OpenDream.Compilation.managed_compile(cenv)

    renv = env.branch()
    DMShared.OpenDream.Compilation.load_compile(cenv, renv)
    return renv

async def random_ast(env):
    result = {}
    generate_ast(env)
    unparse_test(env)
    env.attr.benv = await byond_compilation(env)
    env.attr.oenv = await opendream_compilation(env)
    return result

async def test_opendream(env):
    env.attr.ast.builder = DreamCollider.OpenDreamBuilder( )
    await random_ast(env)
    env.attr.task.finished = True

async def test_byond(env):
    env.attr.ast.builder = DreamCollider.ByondBuilder( )
    await random_ast(env)
    env.attr.task.finished = True

async def test_byond_experimental(env):
    env.attr.ast.builder = DreamCollider.ByondBuilderExperimental( )
    await random_ast(env)
    env.attr.task.finished = True

def marshall_test(env):
    test = {}
    test["ast"] = DreamCollider.AST.marshall( env.attr.ast.ast )
    test["tokens"] = DreamCollider.Shape.marshall( env.attr.ast.ast_tokens )
    test["ngrams"] = env.attr.ast.ngram_info
    return test

def unmarshall_test(env):
    env.attr.ast.ast = DreamCollider.AST.unmarshall( env.attr.ast.data["ast"] )
    env.attr.ast.ast_tokens = list(DreamCollider.Shape.unmarshall( env.attr.ast.data["tokens"], env.attr.ast.ast))
    env.attr.ast.ngram_info = env.attr.ast.data["ngrams"]

def unparse_test(env):
    upar = DreamCollider.Unparser()
    env.attr.ast.text = upar.unparse(env.attr.ast.ast_tokens)   

import DMShared, DreamCollider

genv = Shared.Environment()
benv = genv.branch()
oenv = genv.branch()
