from macropy.core_tests.basic_decorator_macro import macros, my_macro

def outer(x):
    return x
def inner(x):
    return x

@outer
@my_macro
@inner
def run():
    x = 10
    x = x + 1
    return x