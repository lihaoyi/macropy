import re

from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, u, ast_list

macros = Macros()

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

    result = hq[u[new_string] % tuple(ast_list[list(map(parse_expr, captured))])]

    return result
