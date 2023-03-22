
from .imports import *
from .env import *

### tasks
def new_task(fn, *args, **kwargs):
    pending_tasks.append( (fn, args, kwargs) )

def async_thread_launch():
    asyncio.run( async_thread_main() )

async def async_thread_main():
    global pending_tasks, tasks
   
    while True:
        for fn, args, kwargs in pending_tasks:
            tasks.add( asyncio.create_task( fn(*args, **kwargs) ) )
        pending_tasks = []

        try:
            for co in asyncio.as_completed(tasks, timeout=0.1):
                await co
        except TimeoutError:
            pass
        
        remaining_tasks = set()
        for task in tasks:
            if not task.done():
                remaining_tasks.add( task )
            else:
                pass
        tasks = remaining_tasks
        
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
async def byond_compilation(config_env, cenv):
    cenv.attr.compilation.root_dir = config_env.attr.ram_dir / 'byond_compilation' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.Byond.Compilation.managed_compile(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

# compilation
async def byond_objtree(config_env, cenv):
    cenv.attr.compilation.root_dir = config_env.attr.ram_dir / 'byond_compilation' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.Byond.Compilation.managed_objtree(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

async def opendream_compilation(config_env, cenv):
    cenv.attr.compilation.root_dir = config_env.attr.ram_dir / 'opendream_compilation' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.OpenDream.Compilation.managed_compile(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

def base_env(verbose=False):
    root_env = Shared.Environment()
    root_env_t = EnvTracker(root_env, "root_env")

    setup_base(root_env)
    if verbose:
        root_env_t.print("1")

    config_env = root_env.branch()
    config_env.attr.config = open_config()
    config_env_t = EnvTracker(config_env, "config_env")

    load_config(config_env)
    if verbose:
        config_env_t.print("2")
    load_paths(root_env, config_env)

    root_env.attr.config = config_env

    return root_env

def generate_dmsource(root_env, verbose=False):
    collider_env = root_env.branch()
    collider_env_t = EnvTracker(collider_env, "collider_env")
    builder_experimental(collider_env)
    if verbose:
        collider_env_t.print("1")
    generate_ast(collider_env)
    if verbose:
        collider_env_t.print("2")
    tokenize_ast(collider_env)
    if verbose:
        collider_env_t.print("3")
    unparse_ast(collider_env)
    if verbose:
        collider_env_t.print("4")
    compute_ngrams(collider_env)
    if verbose:
        collider_env_t.print("5")

    return collider_env

def load_byond_install(root_env, verbose=False):
    benv = root_env.branch()
    benv_t = EnvTracker(benv, "benv")
    for prop in list(root_env.attr.config.filter_properties(".byond_main.*")):
        root_env.attr.config.rebase(".byond_main", ".install", prop, new_env=benv, copy=True)
    if verbose:
        benv_t.print("1")
    return benv

async def compile_with_byond(root_env, collider_env, benv, verbose=False):
    cenv = benv.branch()
    cenv_t = EnvTracker(cenv, "cenv")
    cenv.attr.compilation.dm_file = collider_env.attr.collider.text
    DMShared.pipe_stdout(cenv)
    await byond_compilation(root_env, cenv)
    cenv.attr.compile.stdout_text = cenv.attr.compile.stdout.getvalue()
    DMShared.pipe_stdout(cenv)
    await byond_objtree(root_env, cenv)
    cenv.attr.objtree.stdout_text = cenv.attr.objtree.stdout.getvalue()
    if verbose:
        cenv_t.print("1")
    return cenv

async def dmsource_all_tasks(root_env, verbose=False):
    collider_env = generate_dmsource(root_env, verbose)
    benv = load_byond_install(root_env, verbose)
    cenv = await compile_with_byond(root_env, collider_env, benv, verbose)

    DMShared.Byond.Compilation.parse_compile_stdout( cenv )

    renv = root_env.branch()
    renv.attr.benv = cenv
    return renv

def save_test(env):
    return DMShared.pickle_env(env, ['.compilation.dm_file', '.compile.stdout_text', '.objtree.stdout_text', '.compile.stdout_parsed'])

def load_test(env, data):
    return DMShared.unpickle_env(env, data)

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