
import os, asyncio
import Shared

class Install(object):
    @staticmethod
    def set_current(config, _id):
        config['byond.install.id'] = _id
        config["byond.install_dir"] = config['byond.dirs.installs'] / config['byond.install.id']

    @staticmethod
    def parse_byond_version(version):
        components = version.split("_")
        ver_split = components[0].split(".")
        result = {"major":ver_split[0]}
        if len(ver_split) > 1:
            result["minor"] = ver_split[1]
        result["os"] = components[-1]
        return result

    @staticmethod 
    def get_bytecode_file(filename):
        return filename.with_suffix('.dmb')

    @staticmethod
    def download(config, version):
        config['byond.install_dir'] = config['byond.dirs.installs'] / f"{version}"
        zipfile = f"{version}_byond_linux.zip"
        save_path = config['tmp_dir'] / zipfile
        url = f'https://www.byond.com/download/build/{version.split(".")[0]}/{zipfile}'
        if not os.path.exists(config['byond.install_dir']):
            os.system(f"wget {url} -O {save_path}")
            os.system(f"unzip -qq {save_path} -d {config['byond.install_dir']}")

    @staticmethod
    def get_compile_args(args={}):
        preargs = ""
        postargs = ""
        if "code_tree" in args:
            preargs += "-code_tree "
        if "obj_tree" in args:
            preargs += "-o "
        return (preargs, postargs)

    @staticmethod
    def get_run_args(args={}):
        preargs = ""
        postargs = ""
        if "trusted" in args:
            postargs += "-trusted "
        return (preargs, postargs)

    @staticmethod
    async def compile(config, file, args={}):
        config = config.branch('byond_compile')
        preargs, postargs = Install.get_compile_args(args)
        install_dir = config['byond.install_dir']

        config['process.env'] = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        command = f"{install_dir}/byond/bin/DreamMaker {preargs} {file} {postargs}"
        return await Shared.Process.shell(config, command)

    @staticmethod
    async def run(config, file, args={}):
        config = config.branch('byond_run')
        preargs, postargs = Install.get_run_args(args)
        install_dir = config['byond.install_dir']

        config['process.env'] = {'LD_LIBRARY_PATH':f"{install_dir}/byond/bin"}
        command = f"{install_dir}/byond/bin/DreamDaemon {preargs} {file} {postargs}"
        return await Shared.Process.shell(config, command)

    @staticmethod 
    def prepare_code_tree(config, code_tree_prefix):
        config['byond.codetree.prefix'] = code_tree_prefix
        config['byond.codetree.out'] = code_tree_prefix.with_suffix('.out.txt')
        config['byond.codetree.err'] = code_tree_prefix.with_suffix(".err.txt")
        config['byond.codetree.recompile'] = True

    @staticmethod 
    def prepare_obj_tree(config, obj_tree_prefix):
        config['byond.objtree.prefix'] = obj_tree_prefix
        config['byond.objtree.out'] = obj_tree_prefix.with_suffix('.out.txt')
        config['byond.objtree.err'] = obj_tree_prefix.with_suffix(".err.txt")
        config['byond.codetree.recompile'] = True

    @staticmethod
    async def generate_code_tree(config, dm_file_path):
        if config['byond.codetree.recompile'] is False and os.path.exists(config['byond.codetree.out']):
            return
        process = await Install.compile(config, dm_file_path, args={'code_tree':True})
        await asyncio.wait_for(process.wait(), timeout=None)

    @staticmethod
    async def generate_obj_tree(config, dm_file_path, recompile=False):
        if config['byond.objtree.recompile'] is False and os.path.exists(config['byond.objtree.out']):
            return
        process = await Install.compile(config, dm_file_path, args={'obj_tree':True})
        await asyncio.wait_for(process.wait(), timeout=None)

    @staticmethod
    async def generate_empty_code_tree(config, working_dir):
        empty_file_path = working_dir / 'empty.dm'
        if not os.path.exists(empty_file_path):
            with open(empty_file_path, "w") as ef:
                ef.write('\n')

        config = config.branch('generate_empty')
        Install.prepare_code_tree(config, empty_file_path)
        config['process.stdout'] = open(config['byond.codetree.out'], "wb")
        config['process.stderr'] = open(config['byond.codetree.err'], "wb")
        await Install.generate_code_tree(config, empty_file_path)
        config['process.stdout'].close()
        config['process.stderr'].close()

