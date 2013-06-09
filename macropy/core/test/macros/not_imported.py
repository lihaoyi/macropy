from macropy.core.test.macros.not_imported_macro import macros, g
from macropy.core.test.macros.not_imported_macro import f

def run1():
    f = [1, 2, 3, 4, 5]
    g = 1
    return f[g[3]]

def run2():
    return f[g[3]]