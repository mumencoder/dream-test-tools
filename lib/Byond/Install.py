
import os, asyncio
import Shared

class Install(object):
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
    def load(env, _id):
        install = env.prefix('.byond.install')
        install.id = _id
        install.dir = env.attr.byond.dirs.installs / install.id
        info = env.attr.byond.installs[_id]
        install.type = info['type']
        install.version = info["version"]
        install.platform = "byond"

        env.attr.install = env.attr.byond.install

    @staticmethod
    async def ensure(env):
        with Shared.Workflow.status(env, "ensure byond"):
            install = env.prefix('.byond.install')
            if install.type == "web_official":
                await Install.download(env)

    @staticmethod
    async def download(env):
        install = env.prefix('.byond.install')
        zipfile = f"{install.version}_byond_linux.zip"
        save_path = env.attr.dirs.tmp / zipfile
        url = f'https://www.byond.com/download/build/{install.version.split(".")[0]}/{zipfile}'
        if not os.path.exists(install.dir):
            env2 = env.branch()
            env2.attr.shell.command = f"wget {url} -O {save_path}"
            await Shared.Process.shell(env2)
            env2 = env.branch()
            env2.attr.shell.command = f"unzip -qq {save_path} -d {install.dir}"
            await Shared.Process.shell(env2)