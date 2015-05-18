import ast

import macropy.core.macros
from macropy.core.hquotes import macros, hq, unhygienic
from macropy.tracing import macros, show_expanded
from macropy.core import Captured

macros = macropy.core.macros.Macros()

value = 2

def double(x):
    return x * value

@macros.expr
def expand(tree, **kw):
    tree = hq[(lambda cow, prefix: prefix + "x: " + cow(ast_literal[tree]))(double, str(value))]
    return tree


@macros.block
def expand_block(tree, **kw):
    v = 5
    with hq as new_tree:
        x = v
        y = x + v
        z = x + y + v
        return z
    return new_tree

@macros.block
def expand_block_complex(tree, **kw):
    v = 5
    with hq as new_tree:
        x = v
        def multiply(start, *args):
            func = lambda a, b: a * b
            accum = 1
            for a in [start] + list(args):
                accum = func(accum, a)
            return accum
        y = x + v
        z = x + y + v
        return multiply(z, 2, 3, 4)

    return new_tree
