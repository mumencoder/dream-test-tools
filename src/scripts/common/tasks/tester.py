
from ..env import *
from ..imports import *

def reset_test(tenv):
    if os.path.exists( tenv.attr.test.base_dir ):
        shutil.rmtree( tenv.attr.test.base_dir )
    DMShared.DMSource.TestCase.load_test(tenv)
    DMShared.DMSource.TestCase.write(tenv)

async def termination_check(env):
    if os.path.exists( os.path.join(env.attr.shell.dir, 'fin') ):
        return True
    elif Shared.Process.limited_process(env, time_limit=5.0, memory_limit=1*1024**3):
        return True
    return False

def update_testrun(env, testrun_id, results):
    with open( env.attr.dirs.testruns / f'{testrun_id}.pickle', 'wb' ) as f:
        f.write( pickle.dumps(results) ) 

    if os.path.exists( env.attr.dirs.storage / 'metadata' / 'test_runs.json' ):
        with open(env.attr.dirs.storage / 'metadata' / 'test_runs.json', "r") as f:
            test_runs = json.loads(f.read())
    else:
        test_runs = []

    if testrun_id not in test_runs:
        test_runs.append( testrun_id )
        with open(env.attr.dirs.storage / 'metadata' / 'test_runs.json', "w") as f:
            f.write( json.dumps( test_runs ) )

async def tester_byond_compile(env):
    cenv = env.attr.benv.branch()
    cenv.attr.compilation.dm_file = env.attr.collider.text
    Shared.Process.pipe_stdout(cenv)
    await byond_compilation(cenv)
    env.attr.byond.compile.stdout_text = cenv.attr.compile.stdout.getvalue()
    env.attr.byond.compile.returncode = cenv.attr.compile.returncode

    cenv = env.attr.benv.branch()
    cenv.attr.compilation.dm_file = env.attr.collider.text
    Shared.Process.pipe_stdout(cenv)
    await byond_objtree(cenv)
    env.attr.byond.objtree.stdout_text = cenv.attr.objtree.stdout.getvalue()
    env.attr.byond.objtree.returncode = cenv.attr.objtree.returncode

    #env.attr.persist.add( '.compilation.dm_file', '.byond.compile.stdout_text', '.byond.objtree.stdout_text' )

async def tester_opendream_compile(env):
    cenv = env.attr.oenv.branch()
    cenv.attr.compilation.dm_file = env.attr.collider.text
    Shared.Process.pipe_stdout(cenv)
    await opendream_compilation(cenv)
    env.attr.opendream.compile.stdout_text = cenv.attr.compile.stdout.getvalue()
    env.attr.opendream.compile.returncode = cenv.attr.compile.returncode

    #env.attr.presist.add( '.compilation.dm_file', '.opendream.compile.stdout_text' )

async def byond_compilation(cenv):
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.Byond.Compilation.managed_compile(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

async def byond_objtree(cenv):
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.Byond.Compilation.managed_objtree(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

async def opendream_compilation(cenv):
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.OpenDream.Compilation.managed_compile(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

    
import DMShared