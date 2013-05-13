from macropy.core.macros import *
from macropy.core.lift import macros, q
macros = Macros()

@macros.block
def my_macro(tree):
    with q as code:
        x = x / 2
        y = 1 / x
        x = x / 2
        y = 1 / x
        x = x / 2
        y = 1 / x
    return code