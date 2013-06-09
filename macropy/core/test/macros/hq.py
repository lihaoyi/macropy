from macropy.core.test.macros.hq_macro import macros, expand

double = "double"
value = 1
def run():
    return expand[str(value) + " " + double + " "]