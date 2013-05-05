from macropy.core.macros import *

macros = Macros()

@macros.expr
def f(tree):
    return Num(n = 10)