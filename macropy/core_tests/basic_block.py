from macropy.core_tests.basic_block_macro import macros, my_macro

def run():
    x = 10
    with my_macro as y:
        x = x + 1
    return x