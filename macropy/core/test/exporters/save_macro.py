

# Imports added by remove_from_imports.

import macropy.core.macros
import ast

from macropy.core.test import exporters
from macropy.core.hquotes import macros, hq
macros = macropy.core.macros.Macros()

def double(x):
    return x * x
@macros.expr
def f(tree, **kw):
    n = 10
    return hq[double(ast.ast[tree]) + n]
