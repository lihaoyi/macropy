from macropy.core_tests.basic_expr_macro import macros, f

def run():
    f = 10
    return f(1 * max(1, 2, 3))