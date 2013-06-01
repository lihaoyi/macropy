from macropy.core.macros import *
from macropy.core.lift import macros, q, ast, u
macros = Macros()

@macros.expr()
def expand(tree, **kw):
    addition = 10
    return q(lambda x: x * ast(tree) + u(addition))

print "registered"