
import os
import pathlib, shutil

import Shared

class Push(object):
    def __init__(self, folder):
        self.folder = folder

    def __enter__(self):
        self.old_folder = os.getcwd()

        if not os.path.exists(self.folder):
            self.folder.mkdir(parents=True, exist_ok=True)

        os.chdir(self.folder)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.chdir(self.old_folder)

class Path(type(pathlib.Path())):
    def __init__(self, path):
        self.ensure_parent_folder()

    def __add__(self, path):
        newpath = Path( super().__truediv__(path) )
        newpath.ensure_folder()
        return newpath

    def __truediv__(self, path):
        newpath = Path( super().__truediv__(path) )
        return newpath

    def ensure_folder(self):
        if not self.exists():
            self.mkdir(parents=True, exist_ok=True)

    def ensure_parent_folder(self):
        if not self.exists():
            self.parent.mkdir(parents=True, exist_ok=True)

    def ensure_clean_dir(self):
        if os.path.exists(self):
            shutil.rmtree(self)
        if not os.path.exists(self):
            os.mkdir(self)

    @staticmethod            
    async def sync_folders(env, src, dest):
        env = env.branch()
        env.attr.shell.command = f"rsync -r {src}/ {dest}"
        await Shared.Process.shell(env)

    @staticmethod            
    async def full_sync_folders(env, src, dest):
        env = env.branch()
        env.attr.shell.command = f"rsync --delete -r {src}/ {dest}"
        await Shared.Process.shell(env)



