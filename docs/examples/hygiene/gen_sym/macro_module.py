from macropy.core.macros import *
from macropy.dump import macros, dump, dumpid
from macropy.core.quotes import macros, q, u
import pprint
pp = pprint.PrettyPrinter(indent = 4
)
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

    dumpid[tree]
    dumpid[real_repr(tree)]
    dumpid[tree]

    dumpid[new_tree]
    dumpid[real_repr(new_tree)]
    dumpid[unparse(new_tree)]

    return new_tree
