from macropy.core.macros import *
from macropy.core.quotes import macros, q

macros = Macros()
_ = object()



@macros.expr
def f(tree, gen_sym, **kw):

    @Walker
    def underscore_search(tree, collect, **kw):
        if isinstance(tree, Name) and tree.id == "_":
            name = gen_sym()
            tree.id = name
            collect(name)
            return tree

    tree, used_names = underscore_search.recurse_real(tree)

    new_tree = q[lambda: ast[tree]]
    new_tree.args.args = [Name(id = x) for x in used_names]
    return new_tree
