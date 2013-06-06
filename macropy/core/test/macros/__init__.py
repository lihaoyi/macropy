
import unittest
import sys
import macropy.core.macros
from macropy.core.test.macros import exact_src


class Tests(unittest.TestCase):

    def test_hygienic_quotes(self):
        import hygienic_quotes
        assert hygienic_quotes.run() == 10
        print hygienic_quotes.run1()
        assert hygienic_quotes.run1() == 20