import unittest
from macropy.macros.tco import macros
from macropy.macros.tco import tco
from macropy.macros.adt import macros
from macropy.macros.adt import *
from macropy.macros.pattern import macros
from macropy.macros.pattern import *


class Tests(unittest.TestCase):

    def test_tco_basic(self):
        @tco
        def foo(n):
            if n == 0:
                return 1
            return foo(n-1)
        self.assertEquals(1, foo(3000))


    def test_tco_returns(self):

        @case
        class Cons(x, rest): pass

        @case
        class Nil(): pass

        def my_range(n):
            cur = Nil()
            for i in reversed(range(n)):
                cur = Cons(i, cur)
            return cur

        @tco
        def oddLength(xs):
            with switch(xs):
                if Nil():
                    return False
                else:
                    return evenLength(xs.rest)

        @tco 
        def evenLength(xs):
            with switch(xs):
                if Nil():
                    return True
                else:
                    return oddLength(xs.rest)

        self.assertTrue(True, evenLength(my_range(2000)))
        self.assertTrue(True, oddLength(my_range(2001)))
        # if we get here, then we haven't thrown a stack overflow.  success.

    def test_implicit_tailcall(self):
        """Tests for when there is an implicit return None"""
        blah = []

        @tco
        def appendStuff(n):
            if n != 0:
                blah.append(n)
                appendStuff(n-1)

        appendStuff(10000)
        self.assertEquals(10000, len(blah))

    def test_util_func_compatibility(self):
        def util():
            return 3 + 4

        @tco
        def f(n):
            if n == 0:
                return util()
            else:
                return f(n-1)

        self.assertEquals(7, f(1000))

        def util2():
            return None

        @tco
        def f2(n):
            if n == 0:
                return util2()
            else:
                return f2(n-1)

        self.assertEquals(None, f2(1000))

    def test_tailcall_methods(self):

        class Blah(object):
            @tco
            def foo(self, n):
                if n == 0:
                    return 1
                return self.foo(n-1)

        self.assertEquals(1, Blah().foo(5000))


if __name__ == '__main__':
    unittest.main()
