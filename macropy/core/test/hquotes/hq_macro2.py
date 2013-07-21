from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, unhygienic
from macropy.tracing import macros, show_expanded

macros = Macros()

value = 2

def double(x):
    return x * value
#
# @macros.expr
# def expand(tree, gen_sym, **kw):
#     tree = hq[(lambda cow, prefix: prefix + "x: " + cow(ast[tree]))(double, str(value))]
#     return tree


@macros.block
def expand_block(tree, gen_sym, **kw):
    v = 5
    with hq as new_tree:
        x = v
        y = x + v
        z = x + y + v
        return x
    return new_tree