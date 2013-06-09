from macropy.core.macros import *

macros = Macros()

@macros.block
def expand(tree, **kw):
    import copy
    return tree * 10
