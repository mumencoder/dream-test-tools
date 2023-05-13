
from common import *

root_env = base_env()
load_config( root_env, sys.argv[1] )

archive_dir = root_env.attr.dirs.storage / 'byond_archive'
install_dir = root_env.attr.dirs.storage / 'byond_install'

def print_unknowns():
    for filename in os.listdir( archive_dir ):
        result = DMShared.Byond.Download.parse_official_filename( filename )
        if result["type"] == "unknown":
            print( filename )

async def main():
    versions = collections.defaultdict(list)
    for filename in os.listdir( archive_dir ):
        result = DMShared.Byond.Download.parse_official_filename( filename )
        if result["type"] == "byond_linux.zip":
            versions[ result["major"] ].append( result )

    for major, result in versions.items():
        ienv = root_env.branch()    

        version = sorted(result, key=lambda r: r["minor"], reverse=True )[0]

        Shared.Process.pipe_stdout(ienv)
        ienv.attr.install.zip_path = archive_dir / version["filename"]
        ienv.attr.install.dir = install_dir / f'{version["major"]}.{version["minor"]}'
        await DMShared.Byond.Install.from_zip(ienv)

        print(version)

asyncio.run( main() )