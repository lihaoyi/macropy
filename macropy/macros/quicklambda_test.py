import unittest

from macropy.core.macros import *
from macropy.core.lift import *
from macropy.macros.string_interp import *
from macropy.macros.quicklambda import f, _

class Tests(unittest.TestCase):
    def test_basic(self):
        assert map(f%(_ - 1), [1, 2, 3]) == [0, 1, 2]
        assert reduce(f%(_ + _), [1, 2, 3]) == 6

    def test_partial(self):
        basetwo = f%int(_, base=2)
        assert basetwo('10010') == 18

    def test_attribute(self):
        assert map(f%_.split(' ')[0], ["i am cow", "hear me moo"]) == ["i", "hear"]

    def test_no_args(self):
        from random import random
        thunk = f%random()
        assert thunk() != thunk()




