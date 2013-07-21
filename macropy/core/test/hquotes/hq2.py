from macropy.core.test.hquotes.hq_macro2 import macros, expand_block#, expand

double = "double"
value = 1
#
# def run1():
#     return expand[str(value) + " " + double + " "]

def run2():
    x = 1
    with expand_block:
        pass
    return x
