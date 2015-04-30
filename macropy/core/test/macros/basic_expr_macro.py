

# Imports added by remove_from_imports.

import macropy.core
import macropy.core.macros
import _ast


macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, **kw):
    assert macropy.core.unparse(tree) == "(1 * max(1, 2, 3))", macropy.core.unparse(tree)
    return _ast.Num(n = 10)
