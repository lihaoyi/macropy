from macropy.core.test.macros.hygienic_quotes_macro import macros, my_macro
from macropy.tracing import macros, show_expanded

def log(thing):
    # print thing
    return thing * 2

def run():
    return my_macro[10]


def run1():
    return my_macro[log(10)]