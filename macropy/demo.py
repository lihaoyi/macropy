





































"""
Demos
=====

tracing
-------
from macropy.macros2.tracing import macros
from macropy.macros2.tracing import *
with trace:
    x = (1 + 2)
    y = x * x + 7


quicklambda
-------
from macropy.macros.quicklambda import macros, f

print map(f%_[0], ['omg', 'wtf', 'bbq'])
print reduce(f%(_ + _), [1, 2, 3])


adts
-------
from macropy.macros.adt import macros
from macropy.macros.adt import *

@case
class Point(x, y): pass

p = Point(1, 2)

print str(p)
print p.x
print p.y
print Point(1, 2) == Point(1, 2)


pattern matching
-------


peg
-------

"""


