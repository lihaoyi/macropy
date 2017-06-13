import unittest
import sys
import os
pyc_cache_count = 0
pyc_cache_macro_count = 0
from macropy.core.exporters import NullExporter, PycExporter, SaveExporter

class Tests(unittest.TestCase):
    def test_null_exporter(self):
        import pyc_cache
        # every load and reload should re-run both macro and file
        assert (pyc_cache_count, pyc_cache_macro_count) == (1, 1)
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (2, 2)
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (3, 3)

    def test_pyc_exporter(self):
        import macropy

        macropy.exporter = PycExporter()
        import pyc_cache
        assert (pyc_cache_count, pyc_cache_macro_count) == (3, 3)

        # reloading the file should re-run file but not macro
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (4, 3)
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (5, 3)

        # unless you touch the file to bring its mtime up to that of the
        # stored .pyc, in which case the macro gets re-run too
        f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyc_cache.py"), "a")
        f.write(" ")
        f.close()

        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (6, 4)

        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (7, 4)

        f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyc_cache.py"), "a")
        f.write(" ")
        f.close()

        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (8, 5)

    def test_save_exporter(self):
        import macropy

        macropy.exporter = SaveExporter(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exported"), os.path.dirname(os.path.abspath(__file__)))

        # the original code should work
        import save
        assert save.run() == 14

        macropy.exporter = NullExporter()

        # the copy of the code saved in the ./exported folder should work too
        import macropy.core.test.exporters.exported.save as save_exported
        assert save_exported.run() == 14
        import shutil
        shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "exported"))
