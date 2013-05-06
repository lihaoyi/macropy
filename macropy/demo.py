from macropy.macros.string_interp import macros, s
from macropy.macros2.linq import macros, sql
from macropy.macros.quicklambda import macros, f
from macropy.macros2.tracing import macros, trace
from macropy.macros2.tracing import *
from macropy.macros2.peg import macros
from macropy.macros2.peg import *
from macropy.macros.adt import macros

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


print Point(1, 2)
print Point(1, 2) == Point(1, 2)
with require:
    repr(Point(1, 2)) == "Point(1, 2)"
    Point(1, 2) == Point(1, 2)
    Point(1, 2) != Point(1, 3)
    not (Point(1, 2) != Point(1, 2))

