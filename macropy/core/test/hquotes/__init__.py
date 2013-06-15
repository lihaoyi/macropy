import unittest
import sys
import hq

class Tests(unittest.TestCase):
    def test_hq(self):

        assert hq.run1() == "2x: 1 double 1 double "

        assert hq.run2() == 5

        assert hq.run3() == 6