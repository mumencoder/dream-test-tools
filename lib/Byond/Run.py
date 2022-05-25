
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
    async def run(base_env):
        env = base_env.branch()
        run = env.prefix('.run')
        preargs, postargs = Run.get_args(run.args)
        install_dir = env.attr.install.dir

        env.attr.process.env = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        env.attr.shell.command = f"{install_dir}/byond/bin/DreamDaemon {preargs} {run.dm_file_path} {postargs}"
        await Shared.Process.shell(env)

