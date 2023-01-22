
from ..common import *

from . import Builder

async def install_clopendream(env):
    genv = env.branch()
    genv.attr.git.repo.url = os.environ['CLOPENDREAM_REPO']
    genv.attr.git.repo.dir = env.attr.install.dir
    await Shared.Git.Repo.clone(genv)
    await Shared.Git.Repo.init_all_submodules(genv)

    benv = env.branch()
    benv.attr.dotnet.solution.path = env.attr.install.dir
    await Builder.build( benv )

def setup_dotnet(env):
    sys.path.append( str( env.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0') )
    
def copy_dmstandard_clopen(env):
    src = env.attr.envs.clopendream.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'DMStandard'
    dst = env.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'DMStandard'
    if not os.path.exists( dst ):
        shutil.copytree(src , dst)

    src = env.attr.envs.clopendream.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
    dst = env.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
    if not os.path.exists( dst ):
        shutil.copy(src , dst)