
import os, time, asyncio
import Shared

class Run(object):
    @staticmethod
    def get_args(args={}):
        preargs = ""
        postargs = ""
        if "trusted" in args:
            postargs += "-trusted "
        return (preargs, postargs)    

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
    async def run(env):
        penv = env.branch()
        preargs, postargs = Run.get_args(env.attr.run.args)
        install_dir = env.attr.install.dir

        penv.attr.process.env = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        penv.attr.shell.dir = os.path.dirname( penv.attr.run.dm_file_path )
        penv.attr.shell.command = f"{install_dir}/byond/bin/DreamDaemon {preargs} {penv.attr.run.dm_file_path} {postargs}"
        penv.attr.shell.env = os.environ
        await Shared.Process.shell(penv)