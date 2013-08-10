from macropy.core.test.exact_src_macro import macros, f


def run0():
    return f[1 * max(1, 2, 3)]

def run1():
    return f[1 * max((1,'2',"3"))]

def run_block():
    with f as x:
        print("omg")
        print("wtf")
        if 1:
            print('omg')
        else:
            import math
            math.acos(0.123)

    return x
