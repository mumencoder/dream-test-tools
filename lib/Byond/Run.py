
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
    async def run(base_env):
        env = base_env.branch()
        run = env.prefix('.byond.run')
        preargs, postargs = Run.get_args(run.args)
        install_dir = env.attr.byond.install.dir

        env.attr.process.env = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        env.attr.shell.command = f"{install_dir}/byond/bin/DreamDaemon {preargs} {run.dm_file} {postargs}"
        await Shared.Process.shell(env)

