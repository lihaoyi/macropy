from macropy.core.macros import *

macros = Macros()

@macros.block
def my_macro(tree, target, **kw):
    assert unparse(target) == "y"
    assert unparse(tree).strip() == "x = (x + 1)", unparse(tree)
    return tree * 3
