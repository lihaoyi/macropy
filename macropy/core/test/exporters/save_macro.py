import ast

import macropy.core.macros

from macropy.core.test import exporters
from macropy.core.hquotes import macros, hq
macros = macropy.core.macros.Macros()

def double(x):
    return x * x
@macros.expr
def f(tree, **kw):
    n = 10
    return hq[double(ast_literal[tree]) + n]
