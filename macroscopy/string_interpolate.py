
from macros import *
from ast import *
from lift import *
import re


@macro
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
    result = q%((u%new_string) % (ast % out))
    return result


