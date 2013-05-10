import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u

macros = Macros()

@macros.expr
def s(tree):
    captured = []
    new_string = ""
    chunks = re.split("%{(.*?)}", tree.s)
    for i in range(0, len(chunks)):
        if i % 2 == 0:
            new_string += chunks[i]
        else:
            new_string += "%s"
            captured += [chunks[i]]

    result = q%((u%new_string) % tuple(ast_list%map(parse_expr, captured)))

    return result
