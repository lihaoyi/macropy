from macropy.core.test.macros.argument_macros import macros, expr_macro, block_macro, decorator_macro
import math

def run():
    x = expr_macro(1 + math.sqrt(5))[10 + 10 + 10]

    with block_macro(1 + math.sqrt(5)) as y:
        x = x + 1

    @decorator_macro(1 + math.sqrt(5))
    def f():
        pass

    return x