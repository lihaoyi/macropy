from macropy.core.macros import *
from macropy.core.test import exporters
macros = Macros()

@macros.expr
def f(tree, **kw):

    exporters.pyc_cache_macro_count += 1
    return Num(n = 10)
