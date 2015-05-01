import macropy.core.macros

macros = macropy.core.macros.Macros()

@macros.block
def expand(tree, **kw):
    import copy
    return tree * 10
