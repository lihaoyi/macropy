from macropy.core.macros import *

macros = Macros()

@macros.expr()
def g(tree):
    return Num(n = 20)
