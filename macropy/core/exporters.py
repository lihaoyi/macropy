"""Functions that are nice to have but really should be in the python library"""
import os
import shutil
from macropy.core import unparse
class NullExporter(object):
    def __init__(self, root=os.getcwd()):
        pass

    def export_transformed(self, tree, module_name, file_name):
        pass


class SaveExporter(object):
    def __init__(self, directory="exported", root=os.getcwd()):
        self.root = root
        self.directory = directory
        shutil.rmtree(directory, ignore_errors=True)
        shutil.copytree(".", directory)

    def export_transformed(self, tree, module_name, file_name):

        new_path = os.path.join(
            self.root,
            self.directory,
            os.path.relpath(file_name, self.root)
        )

        with open(new_path, "w") as f:
            f.write(unparse(tree))

class PycExporter(object):
    def __init__(self, root=os.getcwd()):
        self.root = root

    def export_transformed(self, tree, module_name, file_name):
        with open(file, 'U') as f:
            try:
                timestamp = long(os.fstat(f.fileno()).st_mtime)
            except AttributeError:
                timestamp = long(os.stat(file).st_mtime)
            codestring = f.read()
            try:
                codeobject = __builtin__.compile(codestring, dfile or file,'exec')
            except Exception,err:
                py_exc = PyCompileError(err.__class__,err.args,dfile or file)
                if doraise:
                    raise py_exc
                else:
                    sys.stderr.write(py_exc.msg + '\n')
                    return
            if cfile is None:
                cfile = file + (__debug__ and 'c' or 'o')
            with open(cfile, 'wb') as fc:
                fc.write('\0\0\0\0')
                wr_long(fc, timestamp)
                marshal.dump(codeobject, fc)
                fc.flush()
                fc.seek(0, 0)
                fc.write(MAGIC)