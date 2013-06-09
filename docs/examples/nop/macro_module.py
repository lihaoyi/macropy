from macropy.core.macros import *

macros = Macros()

@macros.expr
def expand(tree, **kw):
    return tree

