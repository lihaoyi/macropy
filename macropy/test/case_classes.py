from macropy.case_classes import macros, case, enum, enum_new
from macropy.tracing import macros, show_expanded
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
        class Point(x, y):
            if True:
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
    def test_default_values(self):
        @case
        class Point(x | 0, y | 0):
            pass
        assert str(Point()) == "Point(0, 0)"
        assert str(Point(1)) == "Point(1, 0)"
        assert str(Point(1, 2)) == "Point(1, 2)"
        assert str(Point(y = 5)) == "Point(0, 5)"
        assert str(Point(y = 5, x = 7)) == "Point(7, 5)"
    def test_overriding_methods(self):
        @case
        class Point(x, y):
            def __str__(self):
                return "mooo " + super(Point, self).__str__()

            def __init__(self):
                self.x = 10
                self.y = 10

        assert str(Point()) == "mooo Point(10, 10)"

    def test_destructuring(self):
        @case
        class Point(x, y):
            pass

        p = Point(1, 2)
        x, y = p


    def test_enum(self):

        @enum
        class Direction:
            North, South, East, West

        assert Direction(name="North") is Direction.North

        assert repr(Direction.North) == str(Direction.North) == "Direction.North"

        # getting name
        assert Direction.South.name == "South"


        # selecting by id
        assert Direction(id=2) is Direction.East

        # getting id
        assert Direction.West.id == 3


        # `next` and `prev` properties
        assert Direction.North.next is Direction.South
        assert Direction.West.prev is Direction.East

        # `next` and `prev` wrap-around
        assert Direction.West.next is Direction.North
        assert Direction.North.prev is Direction.West

        # `all`
        assert Direction.all == [
            Direction.North,
            Direction.South,
            Direction.East,
            Direction.West
        ]



    def test_multiline_enum(self):
        @enum
        class Direction:
            North
            South
            East
            West

        assert Direction(name="North") is Direction.North
        assert Direction(name="West") is Direction.West

    def test_complex_enum(self):
        @enum
        class Direction(alignment):
            North("Vertical")
            East("Horizontal")
            South("Vertical")
            West("Horizontal")

            @property
            def opposite(self):
                return Direction(id=(self.id + 2) % 4)

            def padded_name(self, n):
                return (" " * n) + self.name + (" " * n)

        # members
        assert Direction.North.alignment == "Vertical"
        assert Direction.East.alignment == "Horizontal"

        # properties
        assert Direction.North.opposite is Direction.South

        # methods
        assert Direction.South.padded_name(2) == "  South  "
