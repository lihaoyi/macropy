import re

from macropy.core.macros import *
from macropy.core.lift import macros, q, u

_ = None  # makes IDE happy

macros = Macros()

@macros.expr
def f(tree):
    names = ('quickfuncvar' + str(i) for i in xrange(100))


    @AggregateWalker
    def underscore_search(tree):
        if isinstance(tree, Name) and tree.id == "_":
            name = names.next()
            tree.id = name
            return tree, [name]
        else:
            return tree, []


    tree, used_names= underscore_search.recurse(tree)

    new_tree = q%(lambda: ast%tree)
    new_tree.args.args = [Name(id = x) for x in used_names]
    return new_tree
