from macropy.core.macros import *

macros = Macros()

@macros.expr()
def f(tree, **kw):
    return Num(n = 10)
