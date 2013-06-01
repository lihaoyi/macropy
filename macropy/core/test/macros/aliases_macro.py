from macropy.core.macros import *
from macropy.core.quotes import macros, q
macros = Macros()

@macros.expr()
def e(tree, exact_src, **kw):
    return Str("omg")

@macros.expr()
def f(tree, exact_src, **kw):
    return Str("wtf")

@macros.expr()
def g(tree, exact_src, **kw):
    return Str("bbq")
