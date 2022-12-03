
from common import *

env = base_setup()
load_opendream(env.attr.envs.opendream)

from DMCompiler import *
from System import *
import System.Threading.Tasks
import System.IO
from System.Collections.Generic import List

#from Content.Tests import DMTests
#from Robust.Shared.IoC import IoCManager
#from OpenDreamRuntime import IDreamManager

def generate_test():
    env = Shared.Environment()
    env.attr.expr.depth = 3
    builder = DreamCollider.FullRandomBuilder( )
    builder.generate( env )
    return builder

async def print_main():
    builder = generate_test()
    print("====================================")
    builder.print( sys.stdout )
    print("====================================")
    print( builder.unparse() )

async def many_main():
    for i in range(0, 10000):
        if i % 1000 == 0:
            print(i)
        builder = generate_test()
        if random.random() < 0.001:
            print("====================================")
            print( builder.unparse() )

async def OD_main():
    async def expr_main():
        gen = TreeGenerator()
        tenv.attr.compilation.dm_file_path = tenv.attr.test.path / "test.dm" 
        tenv.attr.dmtest.test = gen.test_string(env)
        with open(tenv.attr.compilation.dm_file_path, "w") as f:
            f.write( tenv.attr.dmtest.test )

    savedir = os.getcwd()
    os.chdir( str( Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Tests' / 'DMProject' ) )
    tests = DMTests()
    tests.BaseSetup()
    tests.OneTimeSetup()
    os.chdir( savedir )
    dreamman = IoCManager.Resolve[IDreamManager]()

    ct = 0
    while ct == 0:
        tenv = benv.branch()

        test_id = f"{Shared.Random.generate_string(16)}"
        tenv.attr.test.path = Shared.Path( env.attr.collider.config["test_dir"] ) / test_id
        tenv.attr.shell.dir = tenv.attr.test.path

        await expr_main()
        (bcenv, brenv) = await run_byond()
        with Shared.folder.Push( os.getcwd() ):
            (ocenv, orenv) = await run_opendream_pnet()
        result = compare_report(bcenv, brenv, ocenv, orenv)
        if result["match"] is False:
            with open( Shared.Path( env.attr.collider.config["test_dir"] ) / f"{test_id}.txt", "w" ) as f:
                f.write(result["output"])
        shutil.rmtree( tenv.attr.test.path )
        ct += 1
        print(ct)

asyncio.run( many_main() )