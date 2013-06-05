from macropy.core.test.macros.aliases_macro import macros, e, f as f_new


def run_normal():
    return e[1 * max(1, 2, 3)]

def run_aliased():
    return f_new[1 * max((1,'2',"3"))]

def run_ignored():
    return g[1123]
