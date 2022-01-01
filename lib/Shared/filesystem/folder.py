
import os
import pathlib

class Push(object):
    def __init__(self, folder):
        self.folder = folder

    def __enter__(self):
        self.old_folder = os.getcwd()
        os.chdir(self.folder)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.chdir(self.old_folder)

class Path(type(pathlib.Path())):
    def __init__(self, path):
        self.ensure_folder()

    def __truediv__(self, path):
        newpath = Path( super().__truediv__(path) )
        newpath.ensure_folder()
        return newpath

    def ensure_folder(self):
        if not self.exists():
            self.parent.mkdir(parents=True, exist_ok=True)

    def ensure_clean_dir(self):
        if os.path.exists(self):
            shutil.rmtree(self)
        if not os.path.exists(self):
            os.mkdir(self)

    @staticmethod            
    def sync_folders(src, dest):
        os.system(f'rsync -r {src}/ {dest}')


