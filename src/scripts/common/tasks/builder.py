
from ..imports import *
from ..env import *

async def builder_opendream(env):
    env.attr.collider.builder = DreamCollider.OpenDreamBuilder( )

async def builder_byond(env):
    env.attr.collider.builder = DreamCollider.ByondBuilder( )

async def builder_byond_experimental(env):
    env.attr.collider.builder = DreamCollider.ByondBuilderExperimental( )

def generate_ast(env):
    env.attr.collider.builder.build_all( env )
    env.attr.collider.build_stats = env.attr.collider.build_checker.check( env )

def tokenize_ast(env):
    env.attr.collider.fuzzer = DreamCollider.Fuzzer(env)
    env.attr.collider.ast_tokens = list(env.attr.collider.fuzzer.fuzz_shape( env.attr.collider.builder.toplevel.shape() ) )

def unparse_tokens(env):
    env.attr.collider.unparser = DreamCollider.Unparser(env)
    env.attr.collider.text = env.attr.collider.unparser.unparse()   

def compute_ngrams(env):
    env.attr.collider.ngram_info = DreamCollider.NGram.compute_info( env.attr.collider.ast_tokens )

import DMShared, DreamCollider