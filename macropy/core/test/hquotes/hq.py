from macropy.core.test.hquotes.hq_macro import macros, expand, expand_unhygienic, unhygienic

double = "double"
value = 1
def run1():
    return expand[str(value) + " " + double + " "]

def run2():
    x = 1
    with expand:
        x = x + 1
    return x

def run3():
    x = 1
    with expand_unhygienic:
        x = x + 1
    return x

def run_error():
    unhygienic[10]
