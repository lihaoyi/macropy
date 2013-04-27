from macropy.macros.adt import macros, case, NO_ARG

import unittest

class Tests(unittest.TestCase):

    def test_basic(self):

        @case
        class Point(x, y):
            pass

        for x in range(1, 10):
            for y in range(1, 10):
                p = Point(x, y)
                assert(str(p) == repr(p) == "Point(%s, %s)" % (x, y))
                assert(p.x == x)
                assert(p.y == y)
                assert(Point(x, y) == Point(x, y))

    def test_advanced(self):

        @case
        class Point(x, y):
            def length(self):
                return (self.x ** 2 + self.y ** 2) ** 0.5

        assert(Point(3, 4).length() == 5)
        assert(Point(5, 12).length() == 13)
        assert(Point(8, 15).length() == 17)

        a = Point(1, 2)
        b = a.copy(x = 3)
        assert(a == Point(1, 2))
        assert(b == Point(3, 2))
        c = b.copy(y = 4)
        assert(a == Point(1, 2))
        assert(b == Point(3, 2))
        assert(c == Point(3, 4))

    def test_nested(self):
        @case
        class List():
            class Nil: pass
            class Cons(head, tail): pass

            def is_list(self):
                return True
        assert(isinstance(Cons(None, None), List))
        assert(isinstance(Nil(), List))
        assert(Cons(None, None).is_list() == True)
        assert(Nil().is_list() == True)