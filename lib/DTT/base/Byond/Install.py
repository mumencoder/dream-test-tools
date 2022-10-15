
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
    async def download(env):
        install = env.prefix('.install')
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