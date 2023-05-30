
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1] )

async def main():
    clenv = root_env.branch()
    clenv.attr.git.repo.url = 'https://github.com/mumencoder/Clopendream-parser'
    clenv.attr.git.repo.dir = root_env.attr.dirs.clopendream_install

    clenv.attr.process.stdout = sys.stdout
    clenv.attr.process.stdout_mode = None
    await Shared.Git.Repo.freshen(clenv)

    DMShared.ClopenDream.Install.load_install_from_repo(clenv)

    build_metadata = root_env.attr.dirs.storage / 'metadata' / 'clopendream_install_main.pckl' 

    metadata = Shared.maybe_from_pickle( Shared.get_file(build_metadata), default_value={} )
    await DMShared.ClopenDream.Builder.managed_build(clenv, metadata)
    Shared.put_file(build_metadata, pickle.dumps(metadata) )        

asyncio.run( main() )