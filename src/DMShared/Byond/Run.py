
from ..common import *

class Run(object):
    @staticmethod
    def get_args(args={}):
        preargs = ""
        postargs = ""
        if "trusted" in args and args["trusted"] is True:
            postargs += "-trusted "
        return (preargs, postargs)    

    @staticmethod
    def default_args():
        return {"trusted":None}

    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.dmb')

    @staticmethod
    def wait_test_output(env):
        path = os.path.join( env.attr.shell.dir, 'test.out.json' )
        return os.path.exists( path ) and os.stat( path ).st_mtime > env.attr.process.start_time

    @staticmethod
    async def wait_run_complete(env):
        kill_proc = False
        while env.attr.process.instance.returncode is None:
            if time.time() - env.attr.process.start_time > 2.0 or env.attr.run.exit_condition(env):
                kill_proc = True
            if kill_proc:
                try:
                    env.attr.process.instance.kill()
                    await asyncio.wait_for(env.attr.process.instance.wait(), timeout=0.500)
                except asyncio.exceptions.TimeoutError:
                    pass
            try:
                await asyncio.wait_for(env.attr.process.instance.wait(), timeout=0.050)
            except asyncio.exceptions.TimeoutError:
                pass

    @staticmethod
    async def invoke_server(env):
        penv = env.branch()
        preargs, postargs = Run.get_args(env.attr.run.args)
        install_dir = env.attr.install.dir

        penv.attr.process.env = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        penv.attr.shell.dir = os.path.dirname( penv.attr.run.dm_file_path )
        penv.attr.shell.command = f"{install_dir}/byond/bin/DreamDaemon {preargs} {penv.attr.run.dm_file_path} {postargs}"
        penv.attr.shell.env = os.environ
        await Shared.Process.shell(penv)

    async def managed_run(tenv, cenv):
        renv = None
        if cenv.attr.compilation.returncode == 0:
            renv = tenv.branch()
            renv.attr.run.exit_condition = Run.wait_test_output
            renv.event_handlers['process.wait'] = Run.wait_run_complete
            renv.attr.process.stdout = open(renv.attr.test.root_dir / 'byond.run.stdout.txt', "w")
            renv.attr.run.dm_file_path = Run.get_bytecode_file( cenv.attr.compilation.dm_file_path )
            renv.attr.run.args = {'trusted':True}
            await Run.invoke_server(renv)
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