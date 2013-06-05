from macropy.core.test.macros.basic_expr_macro import macros, f

def run():
    f = 10
    return f[1 * max(1, 2, 3)]