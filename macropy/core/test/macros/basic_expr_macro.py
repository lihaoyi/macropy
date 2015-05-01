import ast

import macropy.core
import macropy.core.macros

macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, **kw):
    assert macropy.core.unparse(tree) == "(1 * max(1, 2, 3))", macropy.core.unparse(tree)
    return ast.Num(n = 10)
