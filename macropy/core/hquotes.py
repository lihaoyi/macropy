"""Hygienic Quasiquotes, which pull in names from their definition scope rather
than their expansion scope."""


import ast

import macropy.core
import macropy.core.analysis
import macropy.core.macros
import macropy.core.quotes
import macropy.core.util
import macropy.core.walkers

macros = macropy.core.macros.Macros()

@macropy.core.macros.macro_stub
def unhygienic():
    """Used to delimit a section of a hq[...] that should not be hygienified"""


@macropy.core.util.register(macropy.core.macros.injected_vars)
def captured_registry(**kw):
    return []

@macropy.core.util.register(macropy.core.macros.post_processing)
def post_proc(tree, captured_registry, gen_sym, **kw):
    if captured_registry == []:
        return tree

    unpickle_name = gen_sym("unpickled")
    with macropy.core.quotes.q as pickle_import:
        from pickle import loads as x

    pickle_import[0].names[0].asname = unpickle_name

    import pickle

    syms = [macropy.core.quotes.ast.Name(id=sym) for val, sym in captured_registry]
    vals = [val for val, sym in captured_registry]

    with macropy.core.quotes.q as stored:
        macropy.core.quotes.ast_list[syms] = macropy.core.quotes.name[unpickle_name](macropy.core.quotes.u[pickle.dumps(vals)])

    stored = macropy.core.walkers.ast_ctx_fixer.recurse(stored)

    tree.body = list(map(macropy.core.quotes.ast.fix_missing_locations, pickle_import + stored)) + tree.body

    return tree

@macropy.core.util.register(macropy.core.macros.filters)
def hygienate(tree, captured_registry, gen_sym, **kw):
    @macropy.core.walkers.Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is macropy.core.Captured:
            new_sym = [sym for val, sym in captured_registry if val is tree.val]
            if not new_sym:
                new_sym = gen_sym(tree.name)

                captured_registry.append((tree.val, new_sym))
            else:
                new_sym = new_sym[0]
            return macropy.core.quotes.ast.Name(new_sym, macropy.core.quotes.ast.Load())

    return hygienator.recurse(tree)


@macros.block
def hq(tree, target, **kw):
    tree = macropy.core.walkers.unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = macropy.core.ast_repr(tree)

    return [macropy.core.quotes.ast.Assign([target], tree)]


@macros.expr
def hq(tree, **kw):
    """Hygienic Quasiquote macro, used to quote sections of code while ensuring
    that names within the quoted code will refer to the value bound to that name
    when the code was quoted. Used together with the `u`, `name`, `ast`,
    `ast_list`, `unhygienic` unquotes."""
    tree = macropy.core.walkers.unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = macropy.core.ast_repr(tree)
    return tree


@macropy.core.analysis.Scoped
@macropy.core.walkers.Walker
def hygienator(tree, stop, scope, **kw):
    if type(tree) is macropy.core.quotes.ast.Name and \
            type(tree.ctx) is macropy.core.quotes.ast.Load and \
            tree.id not in scope.keys():

        stop()

        return macropy.core.Captured(
            tree,
            tree.id
        )

    if type(tree) is macropy.core.Literal:
        stop()
        return tree

    res = macropy.core.macros.check_annotated(tree)
    if res:
        id, subtree = res
        if 'unhygienic' == id:
            stop()
            tree.slice.value.ctx = None
            return tree.slice.value

