from macropy.core.macros import *

macros = Macros()

@macros.expr
def f(tree, **kw):
    assert unparse(tree) == "(1 * max(1, 2, 3))", unparse(tree)
    return Num(n = 10)
