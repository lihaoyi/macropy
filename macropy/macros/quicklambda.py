from macropy.core.macros import *
from macropy.core.lift import macros, q

_ = None  # makes IDE happy

macros = Macros()

@macros.expr()
def f(tree):
    names = ('quickfuncvar' + str(i) for i in xrange(100))

    @Walker
    def underscore_search(tree):
        if isinstance(tree, Name) and tree.id == "_":
            name = names.next()
            tree.id = name
            return tree, collect(name)

    tree, used_names = underscore_search.recurse_real(tree)

    new_tree = q%(lambda: ast%tree)
    new_tree.args.args = [Name(id = x) for x in used_names]
    return new_tree
