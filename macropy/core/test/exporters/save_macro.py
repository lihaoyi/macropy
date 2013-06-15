from macropy.core.macros import *
from macropy.core.test import exporters
from macropy.core.hquotes import macros, hq
macros = Macros()

def double(x):
    return x * x
@macros.expr
def f(tree, **kw):
    n = 10
    return hq[double(ast[tree]) + n]
