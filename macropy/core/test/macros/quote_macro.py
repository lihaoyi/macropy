import ast

import macropy.core.macros

from macropy.core.quotes import macros, q
macros = macropy.core.macros.Macros()

@macros.block
def my_macro(tree, **kw):
    with q as code:
        x = x / 2
        y = 1 / x
        x = x / 2
        y = 1 / x
        x = x / 2
        y = 1 / x
    return code
