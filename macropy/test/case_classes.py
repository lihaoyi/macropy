from macropy.case_classes import macros, case

import unittest

class Tests(unittest.TestCase):

    def test_basic(self):

        @case
        class Point(x, y):
            pass

        Point(1, 2)