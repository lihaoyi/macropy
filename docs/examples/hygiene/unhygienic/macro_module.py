# macro_module.py
from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, u, unhygienic

macros = Macros()

@macros.expr
def log(tree, exact_src, **kw):
    new_tree = hq[wrap(unhygienic[log_func], u[exact_src(tree)], ast[tree])]
    return new_tree


def wrap(printer, txt, x):
    printer(txt + " -> " + repr(x))
    return x

@macros.expose_unhygienic
def log_func(txt):
    print txt