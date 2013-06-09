from macropy.core.macros import *
from macropy.core.quotes import macros, q
macros = Macros()

@macros.expr
def f(tree, exact_src, **kw):
    return Str(s=exact_src(tree))

@macros.block
def f(tree, exact_src, target, **kw):
    with q as s:
        x = y
    s[0].value = Str(s=exact_src(tree))
    return s