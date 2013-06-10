from macropy.core.macros import *
from macropy.core.quotes import macros, q, u

_ = None  # makes IDE happy

macros = Macros()

@macros.expr
def f(tree, gen_sym, **kw):


    @Walker
    def underscore_search(tree, collect, **kw):
        if isinstance(tree, Name) and tree.id == "_":
            name = gen_sym()
            tree.id = name
            collect(name)
            return tree

    tree, used_names = underscore_search.recurse_collect(tree)

    new_tree = q[lambda: ast[tree]]
    new_tree.args.args = [Name(id = x) for x in used_names]
    return new_tree