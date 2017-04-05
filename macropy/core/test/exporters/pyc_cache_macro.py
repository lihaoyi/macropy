import ast

import macropy.core.macros

from macropy.core.test import exporters
macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, **kw):

    exporters.pyc_cache_macro_count += 1
    return ast.Num(n = 10)
