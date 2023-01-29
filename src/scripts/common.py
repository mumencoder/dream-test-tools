
import os, sys, asyncio, json, io, time, re, pathlib, yaml, collections, random, shutil, gzip

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
    benv = Shared.Environment()
    benv.attr.expr.depth = 3
    builder = DreamCollider.FullRandomBuilder( )
    builder.generate( benv )
    builder.add_proc_paths( benv )

    env.attr.ast.builder = builder
    env.attr.ast.ast = builder.toplevel
    env.attr.ast.fuzzer = DreamCollider.Fuzzer()
    env.attr.ast.ast_tokens = list(env.attr.ast.fuzzer.fuzz_shape( builder.toplevel.shape() ) )
    env.attr.ast.ngram_info = DreamCollider.NGram.compute_info( env.attr.ast.ast_tokens )

def compare_paths(env):
    collider_paths = set()
    for node in env.attr.ast.builder.toplevel.tree.iter_nodes():
        if node.is_stdlib:
            continue
        if len(node.path) == 0:
            continue 
        collider_paths.add( node.path )

    byond_paths = set()
    for node in DMShared.Byond.Compilation.iter_objtree(env):
        byond_paths.add( node["path"] )

    path_mismatch = False
    for path in collider_paths:
        if path not in byond_paths:
            path_mismatch = True
    for path in byond_paths:
        if path not in collider_paths:
            path_mismatch = True

    collider_pathlines = collections.defaultdict(list)
    known_mismatch = None
    for node, line in DreamCollider.Shape.node_lines(env.attr.ast.ast_tokens):
        if type(node) is DreamCollider.AST.ObjectBlock:
            collider_pathlines[line].append( node.resolved_path )
    for node in DMShared.Byond.Compilation.iter_objtree(env):
        if node["path"] not in collider_pathlines[ node["line"] ]:
            known_mismatch = (node["line"], node["path"])

    env.attr.ast.collider_paths = collider_paths
    env.attr.ast.byond_paths = byond_paths
    env.attr.ast.collider_byond_paths_difference = collider_paths.difference( byond_paths )
    env.attr.results.path_mismatch = path_mismatch
    env.attr.results.known_mismatch = known_mismatch 
    env.attr.results.collider_pathlines_text = DMShared.Display.sparse_to_full(
         [{"line":k, "value":v} for k,v in sorted( zip(collider_pathlines.keys(), collider_pathlines.values()), key=lambda e: e[0] )] )

# compilation
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
    result["benv"] = await byond_compilation(env)
    result["oenv"] = await opendream_compilation(env)
    compare_paths(result["benv"])
    return result
    
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
