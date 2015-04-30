

# Imports added by remove_from_imports.

import macropy.core.macros
import ast

from macropy.core.hquotes import macros, hq, unhygienic

macros = macropy.core.macros.Macros()

value = 2

def double(x):
    return x * value

@macros.expr
def expand(tree, gen_sym, **kw):
    tree = hq[str(value) + "x: " + double(ast.ast[tree])]
    return tree

@macros.block
def expand(tree, gen_sym, **kw):
    v = 5
    with hq as new_tree:
        return v
    return new_tree

@macros.block
def expand_unhygienic(tree, gen_sym, **kw):

    v = 5
    with hq as new_tree:
        unhygienic[x] = unhygienic[x] + v

    return new_tree
