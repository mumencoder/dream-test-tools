
import sys, os, io, time, asyncio, pathlib
import pymongo, yaml

sys.path.append( os.path.join( os.path.dirname(__file__),"..","..") )

import Shared, DMShared
from dream_collider import *

with open(os.environ["COLLIDER_CONFIG"]) as f:
    config = yaml.safe_load(f)

async def main():
    env = Shared.Environment()

    benv = env.branch()
    benv.attr.version = {
        'full': config["byond"]["version"]["full"], 
        'major': config["byond"]["version"]["major"], 
        'minor': config["byond"]["version"]["minor"]
    }
    benv.attr.install.dir = Shared.Path( config["byond"]["install_dir"] )

    ienv = benv.branch()
    ienv.attr.save_path = Shared.Path( config["tmp_dir"] ) / 'byond.zip'
    await DMShared.Byond.Download.linux(ienv)
    await DMShared.Byond.Install.from_zip(ienv)

    mismatch_ct = 0
    while mismatch_ct < 10:
        cenv = benv.branch()
        cenv.attr.test.path = Shared.Path( config["test_dir"] ) / f"{Shared.Random.generate_string(16)}"
        cenv.attr.compilation.dm_file_path = cenv.attr.test.path / "test.dm" 

        top = Generator.Toplevel( Shared.Environment() )

        s = io.StringIO()
        AST.print( top, s, seen=set() )
        with open( cenv.attr.test.path / "ast.txt", "w") as f:
            f.write( s.getvalue() )
        with open(cenv.attr.compilation.dm_file_path, "w") as f:
            f.write( top.unparse().s.getvalue() )

        cenv.attr.process.stdout = open(cenv.attr.test.path / 'compile.stdout.txt', "w")
        await DMShared.Byond.Compilation.compile(cenv)

        with open(cenv.attr.test.path / "compile.returncode.txt", "w") as f:
            f.write( str(cenv.attr.compilation.returncode) )
        cenv.attr.process.stdout.close()

        if cenv.attr.compilation.returncode == 0 and top.get_error_count() == 0:
            result = "match"
        elif cenv.attr.compilation.returncode != 0 and top.get_error_count() != 0:
            result = "match"
        else:
            result = "mismatch"

        if result == "match":
            shutil.rmtree( cenv.attr.test.path )
        else:
            mismatch_ct += 1



asyncio.run( main() )