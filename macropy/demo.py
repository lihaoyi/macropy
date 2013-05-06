





































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
from macropy.macros.quicklambda import macros, f
from macropy.macros2.peg import macros
from macropy.macros2.peg import *
with peg:
    value = '[0-9]+'.r | ('(', expr, ')')
    op = '+' | '-' | '*' | '/'
    expr = (value, (op, value).rep )

print expr.parse_all("123")
print expr.parse_all("123boo")
print expr.parse_all("((123))")
print expr.parse_all("((123)")
print expr.parse_all("(123+456+789)")
print expr.parse_all("(6/2)")
print expr.parse_all("(1+2+3)+2")
print expr.parse_all("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)")


from macropy.macros.quicklambda import macros, f
from macropy.macros2.peg import macros
from macropy.macros2.peg import *

def reduce_chain(chain):
    chain = list(reversed(chain))
    o_dict = {
        "+": f%(_+_),
        "-": f%(_-_),
        "*": f%(_*_),
        "/": f%(_/_),
    }
    while len(chain) > 1:
        a, [o, b] = chain.pop(), chain.pop()
        chain.append(o_dict[o](a, b))
    return chain[0]

with peg:
    value = '[0-9]+'.r // int | ('(', expr, ')') // (f%_[1])
    op = '+' | '-' | '*' | '/'
    expr = (value is first, (op, value).rep is rest) >> reduce_chain([first] + rest)

print expr.parse_all("123")             #[123]
print expr.parse_all("((123))")         #[123]
print expr.parse_all("(123+456+789)")   #[1368]
print expr.parse_all("(6/2)")           #[3]
print expr.parse_all("(1+2+3)+2")       #[8]
print expr.parse_all("(((((((11)))))+22+33)*(4+5+((6))))/12*(17+5)") #[1804]

@case
class ArithExpr(object):
    class Add(left, right):
        pass

    class Mul(left, right):
        pass

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
