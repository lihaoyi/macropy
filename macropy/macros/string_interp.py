import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u

macros = Macros()

@macros.expr
def s(node):
    captured = []
    new_string = ""
    chunks = re.split("%{(.*?)}", node.s)
    for i in range(0, len(chunks)):
        if i % 2 == 0:
            new_string += chunks[i]
        else:
            new_string += "%s"
            captured += [chunks[i]]

    out = Tuple(elts=[parse_expr(x) for x in captured], ctx=Load())
    result = q%((u%new_string) % (ast%out))
    return result
