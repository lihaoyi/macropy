# macro_module.py
    from macropy.core.macros import *
    from macropy.core.quotes import macros, hq

    macros = Macros

    def double(x):
        return x * 2

    @macros.expr()
    def my_macro(tree, **kw):
        return hq[double(ast[tree])]

# test.py



# macro_module.py
    from macropy.core.macros import *
    from macropy.core.quotes import macros, hq

    macros = Macros

    def double(x):
        return x * 2

    @macros.expr()
    def my_macro(tree, **kw):
        return q[sym1.macros.registered[u[macros.register(double)]](ast[tree])]

# test.py
    from . import macro_module as sym1

    print sym1.macros[0](10)



