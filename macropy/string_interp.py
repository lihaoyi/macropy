import ast
import re

import macropy.core
import macropy.core.macros

from macropy.core.quotes import u, ast_list
from macropy.core.hquotes import macros, hq
from macropy.core import ast_repr, Captured

macros = macropy.core.macros.Macros()

@macros.expr
def s(tree, **kw):
    """Macro to easily interpolate values into string literals."""
    captured = []
    new_string = ""
    chunks = re.split("{(.*?)}", tree.s)
    for i in range(0, len(chunks)):
        if i % 2 == 0:
            new_string += chunks[i]
        else:
            new_string += "%s"
            captured += [chunks[i]]

    result = hq[u[new_string] % tuple(ast_list[list(map(macropy.core.parse_expr, captured))])]

    return result
