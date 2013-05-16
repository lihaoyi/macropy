from macropy.core.macros import *

macros = Macros()

@macros.expr()
def expand(tree):
    return tree

