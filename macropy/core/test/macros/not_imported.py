from macropy.core.test.macros.not_imported_macro import macros, g

def run():
    f = lambda x: x+1
    g = 10
    return f(g(3))