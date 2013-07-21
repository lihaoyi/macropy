from macropy.core.test.hquotes.hq_macro2 import macros, expand_block, expand, expand_block_complex

double = "double"
value = 1

def run1():
    return expand[str(value) + " " + double + " "]

def run2():
    x = 1
    with expand_block:
        pass
    return x

def run3():
    x = 1
    with expand_block_complex:
        pass
    return x
