import unittest
import macropy.core.macros

class Tests(unittest.TestCase):
    def test_basic_identification_and_expansion(self):
        import file_a
        assert file_a.run() == 10

    def test_ignore_macros_not_explicitly_imported(self):
        import file_b
        assert file_b.run() == 10

