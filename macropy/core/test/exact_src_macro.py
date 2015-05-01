import ast

import macropy.core.macros
from macropy.core.quotes import macros, q

macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, exact_src, **kw):
    return ast.Str(s=exact_src(tree))

@macros.block
def f(tree, exact_src, target, **kw):
    with q as s:
        x = y
    s[0].value = ast.Str(s=exact_src(tree))
    return s
