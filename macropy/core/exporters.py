"""Functions that are nice to have but really should be in the python library"""
import os
import shutil
from macropy.core import unparse
from py_compile import wr_long
import marshal
import imp
class NullExporter(object):
    def __init__(self, root=os.getcwd()):
        pass

    def export_transformed(self, code, tree, module_name, file_name):
        pass

    def find(self, file, pathname, description, module_name, package_path):
        pass

class SaveExporter(object):
    def __init__(self, directory="exported", root=os.getcwd()):
        self.root = root
        self.directory = directory
        shutil.rmtree(directory, ignore_errors=True)
        shutil.copytree(".", directory)

    def export_transformed(self, code, tree, module_name, file_name):

        new_path = os.path.join(
            self.root,
            self.directory,
            os.path.relpath(file_name, self.root)
        )

        with open(new_path, "w") as f:
            f.write(unparse(tree))

    def find(self, file, pathname, description, module_name, package_path):
        pass

suffix = __debug__ and 'c' or 'o'
class PycExporter(object):
    def __init__(self, root=os.getcwd()):
        self.root = root

    def export_transformed(self, code, tree, module_name, file_name):
        f = open(file_name + suffix , 'wb')
        f.write('\0\0\0\0')
        timestamp = long(os.fstat(f.fileno()).st_mtime)
        wr_long(f, timestamp)
        marshal.dump(code, f)
        f.flush()
        f.seek(0, 0)
        f.write(imp.get_magic())

    def find(self, file, pathname, description, module_name, package_path):

        try:
            f = open(file.name + suffix, 'rb')
            x = imp.load_compiled(module_name, pathname + suffix, f)
            return x
        except Exception, e:
            print e
