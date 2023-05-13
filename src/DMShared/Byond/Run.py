
from ..common import *

class Run(object):
    @staticmethod
    def create_dreamserver_command(penv):
        if not penv.has_attr('.run.args'):
            args = []
        else:
            args = penv.attr.run.args
        preargs = []
        postargs = []
        for arg in args:
            if arg == "trusted":
                postargs.append("-trusted")

        if penv.has_attr('.run.dmb_file_path'):
            file_path = penv.attr.run.dmb_file_path
        else:
            file_path = ''

        return preargs + [file_path] + postargs

    @staticmethod
    def default_environ(env):
        if not env.has_attr('.shell.env'):
            env.attr.shell.env = dict(os.environ)
        if "LD_LIBRARY_PATH" not in env.attr.shell.env:
            env.attr.shell.env.update( {'LD_LIBRARY_PATH':f"{env.attr.install.dir}/byond/bin"} )

    @staticmethod
    def prepare_from_compilation(env, cenv):
        env.attr.run.dmb_file_path = Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )

    @staticmethod
    async def managed_run(env):
        renv = env.branch()

        Shared.Process.pipe_stdout(renv)
        renv.attr.shell.dir = Shared.Path( os.path.dirname( env.attr.run.dmb_file_path ))

        runlog_path = renv.attr.shell.dir / 'runlog.out'
        runlog = open( runlog_path, "wb" )
        renv.attr.process.stdout = runlog
        renv.attr.process.stdout_mode = None
        renv.attr.process.stderr = runlog
        renv.attr.process.stderr_mode = None
        renv.attr.run.args = ["trusted"]
        renv.attr.shell.program = f'{renv.attr.install.dir}/byond/bin/DreamDaemon'
        renv.attr.shell.args = Run.create_dreamserver_command( renv )

        renv.attr.process.try_terminate = Run.wait_run_complete
        Run.default_environ( renv )
        await Shared.Process.shell(renv)

        runlog.close()
        with open(runlog_path, "rb") as runlog:
            env.attr.run.stdout = runlog.read()
        if os.path.exists(runlog_path):
            os.remove(runlog_path)
        env.attr.run.returncode = renv.attr.process.instance.returncode
    
    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.dmb')

    @staticmethod
    async def wait_run_complete(env):
        if time.time() - env.attr.process.start_time > 2.0:
            return True
        else:
            return False