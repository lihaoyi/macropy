

# Imports added by remove_from_imports.

import macropy.core.macros
import _ast

from macropy.core.test import exporters
macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, **kw):

    exporters.pyc_cache_macro_count += 1
    return _ast.Num(n = 10)
