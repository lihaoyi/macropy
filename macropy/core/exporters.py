"""Ways of dealing with macro-expanded code, e.g. caching or re-serializing it."""
import os
import shutil
from macropy.core import unparse
import marshal
import imp

def wr_long(f, x):
    """Internal; write a 32-bit int to a file in little-endian order."""
    f.write(chr( x        & 0xff))
    f.write(chr((x >> 8)  & 0xff))
    f.write(chr((x >> 16) & 0xff))
    f.write(chr((x >> 24) & 0xff))

class NullExporter(object):
    def export_transformed(self, code, tree, module_name, file_name):
        pass

    def find(self, file_path, pathname, description, module_name, package_path):
        pass

class SaveExporter(object):
    def __init__(self, directory="exported", root=os.getcwd()):
        self.root = root
        self.directory = directory
        shutil.rmtree(directory, ignore_errors=True)
        shutil.copytree(root, directory)

    def export_transformed(self, code, tree, module_name, file_name):

        new_path = os.path.join(
            self.root,
            self.directory,
            os.path.relpath(file_name, self.root)
        )

        with open(new_path, "w") as f:
            f.write(unparse(tree))

    def find(self, file_path, pathname, description, module_name, package_path):
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

    def find(self, file_path, pathname, description, module_name, package_path):

        try:
            file = open(file_path, 'rb')
            f = open(file.name + suffix, 'rb')
            py_time = os.fstat(file.fileno()).st_mtime
            pyc_time = os.fstat(f.fileno()).st_mtime

            if py_time > pyc_time:
                return None
            x = imp.load_compiled(module_name, pathname + suffix, f)
            return x
        except Exception as e:
            print(e)
