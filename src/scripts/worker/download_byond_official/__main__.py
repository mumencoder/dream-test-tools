
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1] )

archive_dir = root_env.attr.dirs.storage / 'byond_archive'

async def latest():
    pass

async def all():
    downloads = 0

    DMShared.Byond.Download.from_official_source(root_env)
    DMShared.Byond.Download.fetch_version_directory(root_env)
    for fileinfo in DMShared.Byond.Download.fetch_version_files(root_env):
        if os.path.exists( archive_dir / fileinfo["file"] ):
            print( "skip", fileinfo["file"] )
            continue
        print( "download", fileinfo["url"] )
        result = requests.get( fileinfo["url"] )
        if result.status_code == 200:
            with open( archive_dir / fileinfo["file"], "wb" ) as f:
                f.write( result.content )
            downloads += 1
        else:
            raise Exception(result.status_code)
        time.sleep(5.0)
    print("downloaded", downloads)

asyncio.run( globals()[sys.argv[2]] )
