
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
    async def create_server_command(env):
        return [
            f"--cvar", 
            f"opendream.json_path={env.attr.run.json_file_path}",
            f"--cvar",
            f"net.port={await Run.get_port()}",
        ]
    
    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.json')

    @staticmethod
    def get_exe_path(env):
        paths = []
        for root_dir, dirs, files in os.walk(env.attr.install.dir):
            for filename in files:
                if filename == "OpenDreamServer":
                    path = os.path.join(root_dir, filename)
                    paths.append(path)
        return paths

    @staticmethod 
    def find_server_binary(env):
        exe_paths = Run.get_exe_path(env)
        if len(exe_paths) != 1:
            raise Exception("missing/ambiguous path", exe_paths)
        env.attr.opendream.server_binary = exe_paths[0]

    @staticmethod
    def prepare_from_compilation(env, cenv):
        env.attr.run.json_file_path = Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )

    async def managed_run(env):
        renv = env.branch()

        Shared.Process.pipe_stdout(renv)
        renv.attr.shell.dir = Shared.Path( os.path.dirname( env.attr.run.json_file_path))

        runlog_path = renv.attr.shell.dir / 'runlog.out'
        runlog = open( runlog_path, "wb" )
        renv.attr.process.stdout = runlog
        renv.attr.process.stdout_mode = None
        renv.attr.process.stderr = runlog
        renv.attr.process.stderr_mode = None

        if not renv.has_attr('.opendream.server_binary'):
            Run.find_server_binary(renv)

        renv.attr.run.args = {}
        renv.attr.shell.program = renv.attr.opendream.server_binary
        renv.attr.shell.args = await Run.create_server_command( renv )

        renv.attr.process.try_terminate = Run.wait_run_complete
        renv.attr.shell.env = os.environ
        await Shared.Process.shell(renv)

        runlog.close()
        with open(runlog_path, "rb") as runlog:
            env.attr.run.stdout = runlog.read()
        if os.path.exists(runlog_path):
            os.remove(runlog_path)
        env.attr.run.returncode = renv.attr.process.instance.returncode

    @staticmethod
    async def wait_run_complete(env):
        if time.time() - env.attr.process.start_time > 10.0:
            return True
        else:
            return False
                
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