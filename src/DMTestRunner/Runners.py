
from .common import *

async def compile_byond(tenv):
    cenv = tenv.branch()

    cenv.attr.process.stdout = open(tenv.attr.test.root_dir / 'byond.compile.stdout.txt', "w")
    await DMShared.Byond.Compilation.compile(cenv)
    with open(tenv.attr.test.root_dir / 'byond.compile.stdout.txt', "r") as f:
        cenv.attr.compilation.log = f.read()

    with open(tenv.attr.test.root_dir / "byond.compile.returncode.txt", "w") as f:
        f.write( str(cenv.attr.compilation.returncode) )
    cenv.attr.process.stdout.close()

    return cenv

async def run_byond(tenv, cenv):
    renv = None
    if cenv.attr.compilation.returncode == 0:
        renv = tenv.branch()
        renv.attr.run.exit_condition = DMShared.Byond.Run.wait_test_output
        renv.event_handlers['process.wait'] = DMShared.Byond.Run.wait_run_complete
        renv.attr.process.stdout = open(renv.attr.test.root_dir / 'byond.run.stdout.txt', "w")
        renv.attr.run.dm_file_path = DMShared.Byond.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        renv.attr.run.args = {'trusted':True}
        await DMShared.Byond.Run.run(renv)
        renv.attr.process.stdout.close()
        with open(renv.attr.test.root_dir / 'byond.run.stdout.txt', "r") as f:
            renv.attr.run.log = f.read()
        if os.path.exists( renv.attr.test.root_dir / 'test.out.json'):
            with open( renv.attr.test.root_dir / 'test.out.json', "r" ) as f:
                try:
                    renv.attr.run.output = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            os.remove( renv.attr.test.root_dir / 'test.out.json')

    return renv

async def compile_opendream(tenv):
    cenv = tenv.branch()

    cenv.attr.build.dir = cenv.attr.install.dir / 'DMCompiler'
    cenv.attr.process.stdout = open(cenv.attr.test.root_dir / 'opendream.compile.stdout.txt', "w")
    await DMShared.OpenDream.Compilation.compile( cenv )

    with open(cenv.attr.test.root_dir / "opendream.compile.returncode.txt", "w") as f:
        f.write( str(cenv.attr.compilation.returncode) )
    cenv.attr.process.stdout.close()

    return cenv

async def run_opendream(tenv):
    cenv = tenv.branch()
    if cenv.attr.compilation.returncode == 0:
        renv = tenv.branch()
        renv.attr.build.dir = Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Server'
        renv.attr.process.stdout = open(renv.attr.test.root_dir / 'opendream.run.stdout.txt', "w")
        renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        renv.attr.run.args = {}
        await DMShared.OpenDream.Run.run(renv)
        renv.attr.process.stdout.close()
    return renv
    
async def setup_opendream_dotnet():
    savedir = os.getcwd()
    os.chdir( str( Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Tests' / 'DMProject' ) )
    tests = DMTests()
    tests.BaseSetup()
    tests.OneTimeSetup()
    os.chdir( savedir )
    dreamman = IoCManager.Resolve[IDreamManager]()

async def run_opendream_dotnet():
    cenv = tenv.branch()

    tenv.attr.shell.dir = tenv.attr.test.root_dir
    settings = DMCompilerSettings()
    settings.Files = List[String]()
    settings.Files.Add( str(tenv.attr.compilation.dm_file_path) )

    prevout = Console.Out
    stdout = System.IO.StringWriter(System.Text.StringBuilder())
    Console.SetOut(stdout)
    try:
        cenv.attr.compilation.returncode = DMCompiler.Compile(settings)
    except Exception as e:
        cenv.attr.compilation.returncode = False
    Console.SetOut(prevout)
    cenv.attr.compilation.log = stdout.ToString()
    with open( cenv.attr.test.root_dir / 'opendream.compile.stdout.txt', "w" ) as f:
        f.write( cenv.attr.compilation.log )

    renv = None
    if cenv.attr.compilation.returncode is True:
        renv = tenv.branch()
        renv.attr.run.dm_file_path = DMShared.OpenDream.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
        dreamman.LoadJson( str(renv.attr.run.dm_file_path) )

        try:
            t = tests.RunNewTest()
            success = t.Item1
            rval = t.Item2
            renv.attr.run.log = str(t.Item3)
        except Exception as e:
            pass

        if os.path.exists( renv.attr.test.root_dir / 'test.out.json'):
            with open( renv.attr.test.root_dir / 'test.out.json', "r" ) as f:
                try:
                    renv.attr.run.output = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            os.remove( renv.attr.test.root_dir / 'test.out.json')
    
    return (cenv, renv)

