from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, rename
macros = Macros()
print "Start Hygienic Quotes Macro"
@macros.expose()
def log(thing):
    # print thing
    return thing

@macros.expr()
def my_macro(tree, hygienic_names, **kw):
    x = q[log(ast[tree])]

    print unparse_ast(x)
    return x

print "End Hygienic Quotes Macro"