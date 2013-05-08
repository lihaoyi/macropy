
from sqlalchemy import *
from macropy.macros2.linq import macros, sql, query, generate_schema

engine = create_engine("sqlite://")
for line in open("macros2/linq_test_dataset.sql").read().split(";"):
    engine.execute(line.strip())

db = generate_schema(engine)

query_string = sql%((x.name, x.area) for x in db.bbc if x.area > 10000000)
print type(query_string)
print query_string

"""
Demos
=====

tracing
-------
from macropy.macros2.tracing import macros
from macropy.macros2.t  racing import *
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
----------------


LINQ
----
from sqlalchemy import *
from macropy.macros2.linq import macros, sql, generate_schema

engine = create_engine("sqlite://")
for line in open("macros2/linq_test_dataset.sql").read().split(";"):
    engine.execute(line.strip())

db = generate_schema(engine)

results = engine.execute(
    sql%((x.name, x.area) for x in db.bbc if x.area > 10000000)
).fetchall()

results = engine.execute(
    sql%(
        x.name for x in db.bbc
        if x.gdp / x.population > (
            y.gdp / y.population for y in db.bbc
            if y.name == 'United Kingdom'
        )
        if (x.region == 'Europe')
    )
).fetchall()

for line in results: print line




from macropy.macros.adt import macros
from macropy.macros.adt import *
from macropy.macros.pattern import macros
from macropy.macros.pattern import *


@case
class Add(left, right):
    pass

@case
class Mul(left, right):
    pass

@case
class Num(x):
    pass

def compute(expr):
    with switch(expr):
        if Num(n):
            return n
        elif Add(x, y):
            return compute(x) + compute(y)
        elif Mul(x, y):
            return compute(x) * compute(y)
"""
