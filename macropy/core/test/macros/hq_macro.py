from macropy.core.macros import *
from macropy.core.quotes import macros, hq, q

macros = Macros()

value = 2

def double(x):
    return x * value

@macros.expr()
def expand(tree, module_alias, gen_sym, **kw):
    tree = hq[str(value) + "x: " + double(ast[tree])]
    return tree

@macros.block()
def expand(tree, module_alias, gen_sym, **kw):
    v = 5
    with hq as new_tree:
        return v
    return new_tree

@macros.block()
def expand_unhygienic(tree, module_alias, gen_sym, **kw):

    v = 5
    with hq as new_tree:
        unhygienic[x] = unhygienic[x] + v


    return new_tree