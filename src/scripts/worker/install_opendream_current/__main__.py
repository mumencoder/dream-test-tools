
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1], sys.argv[2] )

async def main():
    oenv = root_env.branch()
    oenv.attr.git.repo.url = 'https://github.com/OpenDreamProject/OpenDream'
    oenv.attr.git.repo.dir = root_env.attr.dirs.opendream_install

    oenv.attr.process.stdout = sys.stdout
    oenv.attr.process.stdout_mode = None
    await Shared.Git.Repo.freshen(oenv)

    DMShared.OpenDream.Install.load_install_from_repo(oenv)

    build_metadata = root_env.attr.dirs.storage / 'metadata' / 'opendream_install_main.pckl' 

    metadata = Shared.maybe_from_pickle( Shared.get_file(build_metadata), default_value={} )
    await DMShared.OpenDream.Builder.managed_build(oenv, metadata)
    Shared.put_file(build_metadata, pickle.dumps(metadata) )        

def main():
    byond_version = list(sorted( os.listdir(root_env.attr.dirs.byond_install), reverse=True ))[0]

    benv = root_env.branch()
    benv.attr.install.dir = root_env.attr.dirs.byond_install / byond_version
    benv.attr.process.try_terminate = termination_check
        
asyncio.run( main() )