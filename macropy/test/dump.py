import unittest

from macropy.dump import macros, dump
class Tests(unittest.TestCase):
    def test_basic(self):
        assert dump[1] == '1 ~~> 1'
        assert dump[1 + 2] == '(1 + 2) ~~> 3'
        assert dump[2 + 1] == '(2 + 1) ~~> 3'
        assert dump[3*7  +  7*3] == '((3 * 7) + (7 * 3)) ~~> 42'

    def test_if(self):
        assert dump[42 if None else 43] == '(42 if None else 43) ~~> 43'

    def test_lambda(self):
        assert dump[(lambda x: x * 3 + 3 * x)(7)] == \
            '(lambda x: ((x * 3) + (3 * x)))(7) ~~> 42'
