from macropy.core.test.macros.line_number_macro import macros, expand

def run(x):
    y = 0
    with expand:
        x = x - 1
        y = 1 / x

    return x
