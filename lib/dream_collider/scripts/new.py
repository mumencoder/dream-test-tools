
import sys, os, io, time, asyncio, pathlib
import pymongo, yaml

sys.path.append( os.path.join( os.path.dirname(__file__),"..","..") )

import Shared, DMShared
from dream_collider import *

with open(os.environ["COLLIDER_CONFIG"]) as f:
    config = yaml.safe_load(f)

async def main():
    async def full_main():
        gen = FullGenerator()
        top = gen.Toplevel( Shared.Environment() )
        with open( cenv.attr.test.path / "ast.txt", "w") as f:
            f.write( AST.to_str(top) )
        with open(cenv.attr.compilation.dm_file_path, "w") as f:
            f.write( top.unparse().s.getvalue() )

        cenv, renv = await run_byond()

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

    async def run_byond():
        cenv = tenv.branch()

        cenv.attr.process.stdout = open(cenv.attr.test.path / 'byond.compile.stdout.txt', "w")
        await DMShared.Byond.Compilation.compile(cenv)

        with open(cenv.attr.test.path / "byond.compile.returncode.txt", "w") as f:
            f.write( str(cenv.attr.compilation.returncode) )
        cenv.attr.process.stdout.close()

        if cenv.attr.compilation.returncode == 0:
            renv = tenv.branch()
            renv.attr.process.stdout = open(renv.attr.test.path / 'byond.run.stdout.txt', "w")
            renv.attr.run.dm_file_path = DMShared.Byond.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
            renv.attr.run.args = {}
            await DMShared.Byond.Run.run(renv)
            renv.attr.process.stdout.close()

        return (cenv, renv)

    async def run_opendream():
        cenv = tenv.branch()
        cenv.attr.build.dir = Shared.Path( config["opendream"]["repo_dir"] ) / 'DMCompiler'
        cenv.attr.process.stdout = open(cenv.attr.test.path / 'opendream.compile.stdout.txt', "w")
        await DMShared.OpenDream.Compilation.compile( cenv )
        with open(cenv.attr.test.path / "opendream.compile.returncode.txt", "w") as f:
            f.write( str(cenv.attr.compilation.returncode) )
        cenv.attr.process.stdout.close()

        if cenv.attr.compilation.returncode == 0:
            renv = tenv.branch()
            renv.attr.build.dir = Shared.Path( config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Server'
            renv.attr.process.stdout = open(renv.attr.test.path / 'opendream.run.stdout.txt', "w")
            renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
            renv.attr.run.args = {}
            await DMShared.OpenDream.Run.run(renv)
            renv.attr.process.stdout.close()
        
        return (cenv, renv)

    async def expr_main():
        gen = ExprGenerator()
        tenv.attr.compilation.dm_file_path = tenv.attr.test.path / "test.dm" 
        with open(tenv.attr.compilation.dm_file_path, "w") as f:
            f.write( gen.test() )
        await run_byond()

    env = Shared.Environment()
    env.attr.shell.env = os.environ
    env.attr.process.stdout = sys.stdout

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

    ct = 0
    while ct < 10:
        tenv = benv.branch()
        tenv.attr.test.path = Shared.Path( config["test_dir"] ) / f"{Shared.Random.generate_string(16)}"

        await expr_main()
        ct += 1

asyncio.run( main() )