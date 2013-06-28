# macro_module.py
from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, u

macros = Macros()

@macros.expr
def log(tree, exact_src, **kw):
    new_tree = hq[wrap(u[exact_src(tree)], ast[tree])]
    return new_tree

def wrap(txt, x):
    print txt + " -> " + repr(x)
    return x