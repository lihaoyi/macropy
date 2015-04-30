

# Imports added by remove_from_imports.

import macropy.core.macros
import _ast

from macropy.core.quotes import macros, q
macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, exact_src, **kw):
    return _ast.Str(s=exact_src(tree))

@macros.block
def f(tree, exact_src, target, **kw):
    with q as s:
        x = y
    s[0].value = _ast.Str(s=exact_src(tree))
    return s
