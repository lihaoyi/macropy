from macropy.core.macros import *

macros = Macros()

@macros.block()
def expand(tree):
    import copy
    return tree.body * 10
