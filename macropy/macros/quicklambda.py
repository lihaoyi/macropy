import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u

_ = None  # makes IDE happy

macros = Macros()

@macros.expr
def f(node):
    names = ('quickfuncvar' + str(i) for i in xrange(100))
    used_names = []

    @Walker
    def underscore_search(node):
        if isinstance(node, Name) and node.id == "_":
            name = names.next()
            used_names.append(name)
            node.id = name

        return node

    node = underscore_search.recurse(node)

    new_node = q%(lambda: ast%node)
    new_node.args.args = [Name(id = x) for x in used_names]
    return new_node