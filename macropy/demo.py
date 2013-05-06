from macropy.macros.string_interp import macros, s
from macropy.macros2.linq import macros, sql
from macropy.macros.quicklambda import macros, f
from macropy.macros2.tracing import macros, trace
from macropy.macros2.tracing import *
from macropy.macros2.peg import macros
from macropy.macros2.peg import *
from macropy.macros.adt import macros
@case
class Point(x, y):
    pass

print Point(1, 2)
print Point(1, 2) == Point(1, 2)
print repr(Point(1, 2))
