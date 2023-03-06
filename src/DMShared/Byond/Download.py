
from ..common import *

class Download(object):
    @staticmethod
    def get_filenames(env):
        filenames = {}
        full_version = f"{env.attr.install.version.major}.{env.attr.install.version.minor}"
        filenames["byondexe"] = f"{full_version}_byondexe.zip"
        filenames["byond_setup"] = f"{full_version}_byond_setup.zip"
        filenames["byond_linux"] = f"{full_version}_byond_linux.zip"
        filenames["byond.exe"] = f"{full_version}_byond.exe"
        filenames["byond.zip"] = f"{full_version}_byond.zip"
        return filenames

    @staticmethod
    async def linux(env):
        filename = f"{env.attr.install.version.major}.{env.attr.install.version.minor}_byond_linux.zip"
        url = f'https://www.byond.com/download/build/{env.attr.install.version.major}/{filename}'
        if not os.path.exists(env.attr.install.save_path):
            penv = env.branch()
            penv.attr.shell.command = f"wget {url} -O {env.attr.install.save_path}"
            await Shared.Process.shell(penv)