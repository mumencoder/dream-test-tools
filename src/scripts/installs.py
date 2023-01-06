
import os, asyncio, sys

from startup import base_setup
import mumenrepo as Shared
import DMShared

def copy_dmstandard():
    src = baseenv.attr.envs.clopendream.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'DMStandard'
    dst = baseenv.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'DMStandard'
    if not os.path.exists( dst ):
        shutil.copytree(src , dst)

    src = baseenv.attr.envs.clopendream.attr.install.dir / 'OpenDream' / 'DMCompiler' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
    dst = baseenv.attr.envs.clopendream.attr.install.dir / 'ClopenAST' / 'bin' / 'Debug' / 'net7.0' / 'SharpZstd.Interop.dll'
    if not os.path.exists( dst ):
        shutil.copy(src , dst)

copy_dmstandard()
class Byond:
    async def install(env):
        ienv = env.branch()
        ienv.attr.install.save_path = env.attr.dirs.tmp / 'byond.zip'
        await DMShared.Byond.Download.linux(ienv)
        await DMShared.Byond.Install.from_zip(ienv)

class ClopenDream:
    async def install(env):
        genv = env.branch()
        genv.attr.git.repo.url = os.environ['CLOPENDREAM_REPO']
        genv.attr.git.repo.dir = env.attr.install.dir
        await Shared.Git.Repo.clone(genv)
        await Shared.Git.Repo.init_all_submodules(genv)

        benv = env.branch()
        benv.attr.dotnet.solution.path = env.attr.install.dir
        await DMShared.ClopenDream.Builder.build( benv )

class OpenDream:
    async def install(env):
        genv = env.branch()
        genv.attr.git.repo.url = os.environ['OPENDREAM_REPO']
        genv.attr.git.repo.dir = env.attr.install.dir
        await Shared.Git.Repo.clone(genv)
        await Shared.Git.Repo.init_all_submodules(genv)

        benv = env.branch()
        benv.attr.dotnet.solution.path = env.attr.install.dir
        await DMShared.OpenDream.Builder.build( benv )

async def main():
    env = base_setup( Shared.Environment(), sys.argv[1] )
    await Byond.install(env.attr.envs.byond)
    await OpenDream.install(env.attr.envs.opendream)
    await ClopenDream.install(env.attr.envs.clopendream)

asyncio.run( main() )