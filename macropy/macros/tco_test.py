import unittest
from macropy.macros.tco import macros
from macropy.macros.tco import *
from macropy.macros.adt import macros
from macropy.macros.adt import *
from macropy.macros.pattern import macros
from macropy.macros.pattern import *


class Tests(unittest.TestCase):
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

        self.assertTrue(True, evenLength(my_range(20000)))
        self.assertTrue(True, oddLength(my_range(20001)))
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

if __name__ == '__main__':
    unittest.main()
