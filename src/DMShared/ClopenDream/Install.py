
from ..common import *

from . import Builder

class Install(object):
    def load_install_from_repo(env):
        env.attr.install.dir = env.attr.git.repo.dir

    def setup_dotnet(env):
        sys.path.append( str( env.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0') )
    
    def copy_dmstandard_clopen(env):
        src = env.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'DMStandard'
        dst = env.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'DMStandard'
        if not os.path.exists( dst ):
            shutil.copytree(src , dst)

        src = env.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
        dst = env.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
        if not os.path.exists( dst ):
            shutil.copy(src , dst)