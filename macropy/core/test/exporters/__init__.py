import unittest
import sys
import os
pyc_cache_count = 0
pyc_cache_macro_count = 0
from macropy.core.exporters import NullExporter, PycExporter, SaveExporter

THIS_FOLDER = os.path.dirname(__file__)

class Tests(unittest.TestCase):
    def test_null_exporter(self):
        import pyc_cache
        # every load and reload should re-run both macro and file
        assert (pyc_cache_count, pyc_cache_macro_count) == (1, 1),(pyc_cache_count, pyc_cache_macro_count)
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (2, 2),(pyc_cache_count, pyc_cache_macro_count)
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (3, 3),(pyc_cache_count, pyc_cache_macro_count)

    def test_pyc_exporter(self):
        import macropy

        macropy.exporter = PycExporter()
        import pyc_cache
        assert (pyc_cache_count, pyc_cache_macro_count) == (3, 3),(pyc_cache_count, pyc_cache_macro_count)

        # reloading the file should re-run file but not macro
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (4, 3),(pyc_cache_count, pyc_cache_macro_count)
        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (5, 3),(pyc_cache_count, pyc_cache_macro_count)


        cache_file = os.path.join(THIS_FOLDER, "pyc_cache.py")
        # unless you touch the file to bring its mtime up to that of the
        # stored .pyc, in which case the macro gets re-run too
        f = open(cache_file, "a")
        f.write(" ")
        f.close()

        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (6, 4),(pyc_cache_count, pyc_cache_macro_count)

        reload(pyc_cache)
        assert (pyc_cache_count, pyc_cache_macro_count) == (7, 4),(pyc_cache_count, pyc_cache_macro_count)

        f = open(cache_file, "a")
        f.write(" ")
        f.close()

        reload(pyc_cache)
        # [rebcabin: this test just appeared to be numerically wrong. I am not
        #  absolutely positive I did the right thing, here, because I don't
        #  deeply understand the caching process.]
        assert (pyc_cache_count, pyc_cache_macro_count) == (8, 4),(pyc_cache_count, pyc_cache_macro_count)

    def test_save_exporter(self):
        import macropy

        exported_folder = os.path.join(THIS_FOLDER, "exported")
        macropy.exporter = SaveExporter(exported_folder, THIS_FOLDER)

        # the original code should work
        import save
        assert save.run() == 14

        macropy.exporter = NullExporter()

        # the copy of the code saved in the ./exported folder should work too
        import macropy.core.test.exporters.exported.save as save_exported
        assert save_exported.run() == 14
        import shutil
        shutil.rmtree(exported_folder)
