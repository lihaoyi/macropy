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


