
import os, sys, asyncio, json, io, time, re, pathlib, yaml, collections, random, shutil, gzip

import requests 

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

import fastapi
import redis

import mumenrepo as Shared

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

def generate_ast():
    benv = Shared.Environment()
    benv.attr.expr.depth = 3
    builder = DreamCollider.FullRandomBuilder( )
    builder.generate( benv )

    renv = Shared.Environment()
    renv.attr.ast.ast = builder.toplevel
    fuzzer = DreamCollider.Fuzzer()
    renv.attr.ast.ast_tokens = list(fuzzer.fuzz_shape( builder.toplevel.shape() ) )
    renv.attr.ast.ngram_info = DreamCollider.NGram.compute_info( renv.attr.ast.ast_tokens )

    return renv

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