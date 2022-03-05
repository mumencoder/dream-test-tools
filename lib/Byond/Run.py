
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

    @staticmethod
    async def generate_empty_code_tree(config, working_dir):
        empty_file_path = working_dir / 'empty.dm'
        if not os.path.exists(empty_file_path):
            with open(empty_file_path, "w") as ef:
                ef.write('\n')

        config = config.branch('generate_empty')
        run.out, run.err = Shared.Process.split_stream_filename(empty_file_path)
        config['process.stdout'] = open(config['byond.codetree.out'], "wb")
        config['process.stderr'] = open(config['byond.codetree.err'], "wb")
        await Install.generate_code_tree(config, empty_file_path)
        config['process.stdout'].close()
        config['process.stderr'].close()