
from ..common import *

class Run(object):
    base_port = 25566
    port_lock = asyncio.Lock()
    current_port = 0

    @staticmethod
    async def get_port():
        async with Run.port_lock:
            Run.current_port = (Run.current_port + 1) % 5000
        return Run.current_port + Run.base_port

    @staticmethod
    def convert_args(args):
        return ""

    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.json')

    @staticmethod
    def get_exe_path(env):
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.build.dir):
            for filename in files:
                if filename == "OpenDreamServer":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod 
    async def run(env):
        run = env.attr.run
        env = env.branch()
        exe_paths = Run.get_exe_path(env)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", exe_paths)
        cmd = f"{exe_paths[0]} {Run.convert_args(run.args)} "
        cmd += f"--cvar opendream.json_path={run.dm_file_path} "
        cmd += f"--cvar net.port={await Run.get_port()} "
        env.attr.shell.command = cmd
        env.attr.shell.dir = env.attr.build.dir
        await Shared.Process.shell(env)

    async def run_opendream(tenv):
        cenv = tenv.branch()
        if cenv.attr.compilation.returncode == 0:
            renv = tenv.branch()
            renv.attr.build.dir = Shared.Path( env.attr.collider.config["opendream"]["repo_dir"] ) / 'bin' / 'Content.Server'
            renv.attr.process.stdout = open(renv.attr.test.root_dir / 'opendream.run.stdout.txt', "w")
            renv.attr.run.dm_file_path = Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
            renv.attr.run.args = {}
            await Run.run(renv)
            renv.attr.process.stdout.close()
        return renv
        
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