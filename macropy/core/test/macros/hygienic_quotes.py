from macropy.core.test.macros.hygienic_quotes_macro import macros, my_macro

def log(thing):
    # print thing
    pass

def run():
    return my_macro[10]

