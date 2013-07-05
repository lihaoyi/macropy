import unittest

from macropy.quick_lambda import macros, f, _, lazy, interned

class Tests(unittest.TestCase):
    def test_basic(self):
        assert map(f[_ - 1], [1, 2, 3]) == [0, 1, 2]
        assert reduce(f[_ + _], [1, 2, 3]) == 6

    def test_partial(self):
        basetwo = f[int(_, base=2)]
        assert basetwo('10010') == 18

    def test_attribute(self):
        assert map(f[_.split(' ')[0]], ["i am cow", "hear me moo"]) == ["i", "hear"]

    def test_no_args(self):
        from random import random
        thunk = f[random()]
        assert thunk() != thunk()

    def test_name_collision(self):
        sym0 = 1
        sym1 = 2
        func1 = f[_ + sym0]
        assert func1(10) == 11
        func2 = f[_ + sym0 + _ + sym1]
        assert func2(10, 10) == 23

    def test_lazy(self):
        wrapped = [0]
        def func():
            wrapped[0] += 1
            return wrapped[0]
        thunk = lazy[func()]
        assert thunk() == 1
        assert thunk() == 1
        assert thunk() == 1

    def test_interned(self):
        wrapped = [0]
        def func():
            wrapped[0] += 1
            return wrapped[0]

        def interned_func():
            return interned[func()]

        assert interned_func() == 1
        assert interned_func() == 1
        assert interned_func() == 1