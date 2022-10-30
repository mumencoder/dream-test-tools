
from common import *

env = Shared.Environment()

load_config(env)
load_dotnet(env)

from DMCompiler import *
from System import *
import System.Threading.Tasks
import System.IO
from System.Collections.Generic import List
from Content.Tests import DMTests
from Robust.Shared.IoC import IoCManager
from OpenDreamRuntime import IDreamManager

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
        with open(cenv.attr.test.path / 'byond.compile.stdout.txt', "r") as f:
            cenv.attr.compilation.log = f.read()

        with open(cenv.attr.test.path / "byond.compile.returncode.txt", "w") as f:
            f.write( str(cenv.attr.compilation.returncode) )
        cenv.attr.process.stdout.close()

        renv = None
        if cenv.attr.compilation.returncode == 0:
            renv = tenv.branch()
            renv.attr.run.exit_condition = DMShared.Byond.Run.wait_test_output
            renv.event_handlers['process.wait'] = DMShared.Byond.Run.wait_run_complete
            renv.attr.process.stdout = open(renv.attr.test.path / 'byond.run.stdout.txt', "w")
            renv.attr.run.dm_file_path = DMShared.Byond.Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
            renv.attr.run.args = {'trusted':True}
            await DMShared.Byond.Run.run(renv)
            renv.attr.process.stdout.close()
            with open(renv.attr.test.path / 'byond.run.stdout.txt', "r") as f:
                renv.attr.run.log = f.read()
            if os.path.exists( renv.attr.test.path / 'test.out.json'):
                with open( renv.attr.test.path / 'test.out.json', "r" ) as f:
                    try:
                        renv.attr.run.output = json.load(f)
                    except json.decoder.JSONDecodeError:
                        pass
                os.remove( renv.attr.test.path / 'test.out.json')

        return (cenv, renv)

    async def run_opendream_pnet():
        cenv = tenv.branch()

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
        with open( cenv.attr.test.path / 'opendream.compile.stdout.txt', "w" ) as f:
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

            if os.path.exists( renv.attr.test.path / 'test.out.json'):
                with open( renv.attr.test.path / 'test.out.json', "r" ) as f:
                    try:
                        renv.attr.run.output = json.load(f)
                    except json.decoder.JSONDecodeError:
                        pass
                os.remove( renv.attr.test.path / 'test.out.json')
        
        return (cenv, renv)

    def compare_report(bcenv, brenv, ocenv, orenv):
        result = {}
        output = ""
        output += "=== Test ===\n"
        output += tenv.attr.dmtest.test + "\n"
        if bcenv.attr.compilation.returncode != 0 and ocenv.attr.compilation.returncode is False:
            result["compile_match"] = True
        elif bcenv.attr.compilation.returncode == 0 and ocenv.attr.compilation.returncode is True:
            result["compile_match"] = True
        else:
            result["compile_match"] = False

        if result["compile_match"] is True and bcenv.attr.compilation.returncode == 0:
            if brenv.attr_exists('.run.output') and orenv.attr_exists('.run.output'):
                # TODO: support list, dict
                if type(brenv.attr.run.output) is float and type(orenv.attr.run.output) is float:
                    ratio = brenv.attr.run.output / orenv.attr.run.output
                    if ratio > 0.99 and ratio < 1.01:
                        result["match"] = True
                    else:
                        result["match"] = False
                else:
                    result["match"] = brenv.attr.run.output == orenv.attr.run.output
            elif not brenv.attr_exists('.run.output') and not orenv.attr_exists('.run.output'):
                result["match"] = True
            else:
                result["match"] = False
        elif result["compile_match"] is True:
            result["match"] = True
        else:
            result["match"] = False

        if result["compile_match"] is False:
            output += "=== Byond Compile Log ===\n"
            output += bcenv.attr.compilation.log + '\n'
            output += "=== OpenDream Compile Log ===\n"
            output += ocenv.attr.compilation.log + '\n'
        if result["match"] is False and result["compile_match"] is True:
            if brenv.attr_exists('.run.log'):
                output += "=== Byond Run Log ===\n"
                output += str(brenv.attr.run.log) + '\n'
            if orenv.attr_exists('.run.log'):
                output += "=== OpenDream Run Log ===\n"
                output += str(orenv.attr.run.log) + '\n'
            if brenv.attr_exists('.run.output'):
                output += "=== Byond Run Value ===\n"
                output += str(brenv.attr.run.output) + '\n'
            if orenv.attr_exists('.run.output'):
                output += "=== OpenDream Run Value ===\n"
                output += str(orenv.attr.run.output) + '\n'

        result["output"] = output
        return result

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
        tenv.attr.dmtest.test = gen.test()
        with open(tenv.attr.compilation.dm_file_path, "w") as f:
            f.write( tenv.attr.dmtest.test )

    savedir = os.getcwd()
    os.chdir( str( Shared.Path( config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Tests' / 'DMProject' ) )
    tests = DMTests()
    tests.BaseSetup()
    tests.OneTimeSetup()
    os.chdir( savedir )
    dreamman = IoCManager.Resolve[IDreamManager]()

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
    while True:
        tenv = benv.branch()

        test_id = f"{Shared.Random.generate_string(16)}"
        tenv.attr.test.path = Shared.Path( config["test_dir"] ) / test_id
        tenv.attr.shell.dir = tenv.attr.test.path

        await expr_main()
        (bcenv, brenv) = await run_byond()
        with Shared.folder.Push( os.getcwd() ):
            (ocenv, orenv) = await run_opendream_pnet()
        result = compare_report(bcenv, brenv, ocenv, orenv)
        if result["match"] is False:
            with open( Shared.Path( config["test_dir"] ) / f"{test_id}.txt", "w" ) as f:
                f.write(result["output"])
        shutil.rmtree( tenv.attr.test.path )
        ct += 1
        print(ct)

asyncio.run( main() )