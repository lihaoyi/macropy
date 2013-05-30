from macropy.macros.adt import macros, case

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
                assert((Point(x, y) != Point(x, y)) is False)

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
            def __len__(self):
                return 0

            def __iter__(self):
                return iter([])

            class Nil:
                pass

            class Cons(head, tail):
                def __len__(self):
                    return 1 + len(self.tail)

                def __iter__(self):
                    current = self

                    while len(current) > 0:
                        yield current.head
                        current = current.tail

        assert isinstance(List.Cons(None, None), List)
        assert isinstance(List.Nil(), List)

        my_list = List.Cons(1, List.Cons(2, List.Cons(3, List.Nil())))
        empty_list = List.Nil()

        assert len(my_list) == 3
        assert sum(iter(my_list)) == 6
        assert sum(iter(empty_list)) == 0

    def test_body_init(self):
        @case
        class Point(x, y, [length]):
            self.length = (self.x**2 + self.y**2) ** 0.5

        assert Point(3, 4).length == 5

    def test_varargs_kwargs(self):
        @case
        class PointArgs(x, y, [rest]):
            def extra_count(self):
                return len(self.rest)

        assert PointArgs(3, 4).extra_count() == 0
        assert PointArgs(3, 4, 5).extra_count() == 1
        assert PointArgs(3, 4, 5, 6).extra_count() == 2
        assert PointArgs(3, 4, 5, 6, 7).rest == (5, 6, 7)

        with self.assertRaises(TypeError):
            PointArgs(3, 4, p = 0)


        @case
        class PointKwargs(x, y, {rest}):
            pass
        assert PointKwargs(1, 2).rest == {}
        assert PointKwargs(1, 2, k = 10).rest == {"k": 10}
        assert PointKwargs(1, 2, a=1, b=2).rest == {"a": 1, "b": 2}

        with self.assertRaises(TypeError):
            PointKwargs(3, 4, 4)

        @case
        class PointAll([args], {kwargs}):
            pass
        assert PointAll(1, 2, 3, a=1, b=2, c=3).args == (1, 2, 3)
        assert PointAll(1, 2, 3, a=1, b=2, c=3).kwargs == {"a": 1, "b": 2, "c": 3}