
from .imports import *

### ast generation
def builder_opendream(env):
    env.attr.collider.builder = DreamCollider.OpenDreamBuilder( )

def builder_byond(env):
    env.attr.collider.builder = DreamCollider.ByondBuilder( )

def builder_experimental(env):
    env.attr.collider.builder = DreamCollider.ByondBuilderExperimental( )

def generate_ast(env):
    env.attr.collider.builder.build_all( env )

def tokenize_ast(env):
    env.attr.collider.fuzzer = DreamCollider.Fuzzer(env)
    env.attr.collider.ast_tokens = list(env.attr.collider.fuzzer.fuzz_shape( env.attr.collider.builder.toplevel.shape() ) )

def unparse_ast(env):
    env.attr.collider.unparser = DreamCollider.Unparser(env)
    env.attr.collider.text = env.attr.collider.unparser.unparse()   

def compute_ngrams(env):
    env.attr.collider.ngram_info = DreamCollider.NGram.compute_info( env.attr.collider.ast_tokens )

# installs
async def install_byond(benv):
    benv.attr.process.stdout = io.StringIO()
    benv.attr.process.stderr = benv.attr.process.stdout
    benv.attr.process.piped = True

    await DMShared.Byond.install(benv)

async def install_opendream(oenv):
    oenv.attr.process.stdout = io.StringIO()
    oenv.attr.process.stderr = oenv.attr.process.stdout
    oenv.attr.process.piped = True

    await DMShared.OpenDream.Install.init_repo(oenv)
    await DMShared.OpenDream.Builder.build(oenv)

# compilation
async def byond_compilation(env, benv):
    cenv = benv.branch()
    cenv.attr.compilation.root_dir = env.attr.dirs.tmp / 'random_ast' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( env.attr.collider.text )
    await DMShared.Byond.Compilation.managed_compile(cenv)
    await DMShared.Byond.Compilation.managed_objtree(cenv)

    renv = env.branch()
    DMShared.Byond.Compilation.load_objtree(cenv, renv)
    DMShared.Byond.Compilation.load_compile(cenv, renv)
    return renv

async def opendream_compilation(env, oenv):
    cenv = oenv.branch()
    cenv.attr.compilation.root_dir = env.attr.dirs.tmp / 'random_ast' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( env.attr.collider.text )
    await DMShared.OpenDream.Compilation.managed_compile(cenv)

    renv = env.branch()
    DMShared.OpenDream.Compilation.load_compile(cenv, renv)
    return renv

def marshall_test(env):
    test = {}
    test["ast"] = DreamCollider.AST.marshall( env.attr.collider.ast )
    test["tokens"] = DreamCollider.Shape.marshall( env.attr.collider.ast_tokens )
    test["ngrams"] = env.attr.collider.ngram_info
    return test

def unmarshall_test(env):
    env.attr.collider.ast = DreamCollider.AST.unmarshall( env.attr.collider.data["ast"] )
    env.attr.collider.ast_tokens = list(DreamCollider.Shape.unmarshall( env.attr.collider.data["tokens"], env.attr.collider.ast))
    env.attr.collider.ngram_info = env.attr.collider.data["ngrams"]

import DMShared, DreamCollider