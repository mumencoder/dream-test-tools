
import sys, os, io, time, asyncio
import pymongo, yaml

sys.path.append( os.path.join( os.path.dirname(__file__),"..","..") )

import Shared, DMShared
from dream_collider import *

with open(os.environ["COLLIDER_CONFIG"]) as f:
    config = yaml.safe_load(f)

async def main():
    env = Shared.Environment()
    env.attr.process.stdout = sys.stdout

    benv = env.branch()
    benv.attr.version = {
        'full': config["byond"]["version"]["full"], 
        'major': config["byond"]["version"]["major"], 
        'minor': config["byond"]["version"]["minor"]
    }
    benv.attr.install.dir = Shared.Path( config["byond"]["install_dir"] )

    ienv = benv.branch()
    ienv.attr.save_path = os.path.join( config["tmp_dir"], 'byond.zip' )
    await DMShared.Byond.Download.linux(ienv)
    await DMShared.Byond.Install.from_zip(ienv)

    for i in range(0, 1):
        cenv = benv.branch()
        cenv.attr.compilation.dm_file_path = os.path.join(config["dm_dir"], f"{Shared.Random.generate_string(16)}.dm")

        top = Generator.Toplevel( Shared.Environment() )

        s = io.StringIO()
        AST.print( top, s, seen=set() )
        print( s.getvalue() )

        with open(cenv.attr.compilation.dm_file_path, "w") as f:
            f.write( top.unparse().s.getvalue() )

        await DMShared.Byond.Compilation.compile(cenv)

asyncio.run( main() )