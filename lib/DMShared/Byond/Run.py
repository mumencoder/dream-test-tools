
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
    async def run(env):
        async def wait(eenv):
            start_time = time.time()
            while eenv.attr.process.instance.returncode is None:
                if time.time() - start_time > 2.0:
                    eenv.attr.process.instance.kill()
                try:
                    await asyncio.wait_for(eenv.attr.process.instance.wait(), timeout=0.1)
                except asyncio.TimeoutError:
                    pass

        penv = env.branch()
        penv.event_handlers['process.wait'] = wait
        preargs, postargs = Run.get_args(env.attr.run.args)
        install_dir = env.attr.install.dir

        penv.attr.process.env = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        penv.attr.shell.command = f"{install_dir}/byond/bin/DreamDaemon {preargs} {penv.attr.run.dm_file_path} {postargs}"
        penv.attr.shell.env = os.environ
        await Shared.Process.shell(penv)