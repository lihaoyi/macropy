

# Imports added by remove_from_imports.

import macropy.core.macros
import _ast

from macropy.core.quotes import macros, q
macros = macropy.core.macros.Macros()

@macros.expr
def e(tree, exact_src, **kw):
    return _ast.Str("omg")

@macros.expr
def f(tree, exact_src, **kw):
    return _ast.Str("wtf")

@macros.expr
def g(tree, exact_src, **kw):
    return _ast.Str("bbq")
