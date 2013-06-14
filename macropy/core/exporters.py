"""Functions that are nice to have but really should be in the python library"""
import os
import shutil
from macropy.core import unparse
class NullExporter(object):
    def __init__(self, root = os.getcwd()):
        pass

    def export_transformed(self, tree, module_name, file_name):
        print module_name
        pass


class SaveExporter(object):
    def __init__(self, directory="exported", root = os.getcwd()):
        self.root = root
        self.directory = directory
        shutil.copytree(".", directory)

    def export_transformed(self, tree, module_name, file_name):

        new_path = os.path.join(
            self.root,
            self.directory,
            os.path.relpath(file_name, self.root)
        )

        with open(new_path, "w") as f:
            f.write(unparse(tree))
