from macropy.core.macros import *

from macropy.core.quotes import macros, q, unquote_search, u, ast, ast_list, name

@injected_vars.append
def gen_sym(tree, **kw):
    """Create a generator that creates symbols which are not used in the given
    `tree`. This means they will be hygienic, i.e. it guarantees that they will
    not cause accidental shadowing, as long as the scope of the new symbol is
    limited to `tree` e.g. by a lambda expression or a function body"""
    @Walker
    def name_finder(tree, collect, **kw):
        if type(tree) is Name:
            collect(tree.id)
        if type(tree) is Import:
            names = [x.asname or x.name for x in tree.names]
            map(collect, names)
        if type(tree) is ImportFrom:
            names = [x.asname or x.name for x in tree.names]
            map(collect, names)

    found_names = name_finder.collect(tree)
    names = ("sym" + str(i) for i in itertools.count())
    x = itertools.ifilter(lambda x: x not in found_names, names)
    return lambda: x.next()

