from macropy.core.macros import *

macros = Macros()

@macros.expr
def f(tree, **kw):
    assert unparse_ast(tree) == "(1 * max(1, 2, 3))", unparse_ast(tree)
    return Num(n = 10)
