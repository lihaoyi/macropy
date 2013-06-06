from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, rename
macros = Macros()

@macros.expose()
def log(thing):
    # print thing
    return thing

@macros.expr()
def my_macro(tree, hygienic_names, **kw):
    x = q[log(ast[tree])]
    return x

