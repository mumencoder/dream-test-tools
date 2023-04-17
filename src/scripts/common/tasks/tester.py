
from ..env import *
from ..imports import *

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
    cenv.attr.compilation.root_dir = cenv.attr.ram_dir / 'byond_compilation' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.Byond.Compilation.managed_compile(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

async def byond_objtree(cenv):
    cenv.attr.compilation.root_dir = cenv.attr.ram_dir / 'byond_compilation' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.Byond.Compilation.managed_objtree(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

async def opendream_compilation(cenv):
    cenv.attr.compilation.root_dir = cenv.attr.ram_dir / 'opendream_compilation' / Shared.Random.generate_string(24)
    cenv.attr.compilation.dm_file_path = cenv.attr.compilation.root_dir / 'test.dm'
    with open( cenv.attr.compilation.dm_file_path, "w") as f:
        f.write( cenv.attr.compilation.dm_file )
    await DMShared.OpenDream.Compilation.managed_compile(cenv)
    if os.path.exists( cenv.attr.compilation.root_dir ):
        shutil.rmtree( cenv.attr.compilation.root_dir )

    
import DMShared