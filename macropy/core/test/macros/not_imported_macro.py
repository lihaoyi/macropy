

# Imports added by remove_from_imports.

import macropy.core.macros
import _ast


macros = macropy.core.macros.Macros()

@macros.expr
def g(tree, **kw):
    return _ast.Num(n = 0)

@macros.expr
def f(tree, **kw):
    return _ast.Num(n = 0)
