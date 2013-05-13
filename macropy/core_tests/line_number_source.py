from macropy.core_tests.line_number_macro import macros, expand

def run(x, throw):
    with expand:
        x = x + 1

    if throw:
        raise Exception("lol")

    return x
