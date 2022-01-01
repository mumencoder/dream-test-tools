

import os
import shutil, pathlib

import Shared

class File(type(pathlib.Path())):
    def __init__(self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)
        self.ensure_folder()

    def ensure_folder(self):
        if not self.parent.exists():
            self.parent.mkdir(parents=True, exist_ok=True)

    def stale(source_files, dependent_file):
        dependent_mtime = File.mtime(dependent_file)
        for source_file in source_files:
            if dependent_mtime < File.mtime(source_file):
                return True
        return False

    def refresh(source_file, dest_file):
        if File.stale([source_file], dest_file):
            pathlib.Path( dest_file ).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy( source_file, dest_file )
            return True
        else:
            return False

    def update_symlink(link_from, link_to):
        if os.path.lexists(link_to):
            os.unlink( link_to )
        os.symlink( link_from, link_to )

    def mtime(file):
        if os.path.exists(file):
            return os.stat(file).st_mtime
        else:
            return 0

