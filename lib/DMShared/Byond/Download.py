
import os
import Shared

class Download(object):
    @staticmethod
    def get_filenames(version):
        filenames = {}
        version["byondexe"] = f"{version['full']}_byondexe.zip"
        version["byond_setup"] = f"{version['full']}_byond_setup.zip"
        version["byond_linux"] = f"{version['full']}_byond_linux.zip"
        version["byond.exe"] = f"{version['full']}_byond.exe"
        version["byond.zip"] = f"{version['full']}_byond.zip"
        return filenames

    @staticmethod
    async def linux(env):
        filename = f"{env.attr.version['major']}.{env.attr.version['minor']}_byond_linux.zip"
        url = f'https://www.byond.com/download/build/{env.attr.version["major"]}/{filename}'
        if not os.path.exists(env.attr.save_path):
            penv = env.branch()
            penv.attr.shell.env = os.environ
            penv.attr.shell.command = f"wget {url} -O {env.attr.save_path}"
            await Shared.Process.shell(penv)