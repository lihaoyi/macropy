"""Hygienic Quasiquotes, which pull in names from their definition scope rather
than their expansion scope."""
from macropy.core.macros import *

from macropy.core.quotes import macros, q, unquote_search, u, ast, ast_list, name
from macros import fill_hygienes

macros = Macros()

@singleton
class unhygienic():
    """Used to delimit a section of a hq[...] that should not be hygienified"""
from macros import filters, vars, post_processing

vars["captured_registry"] = {}

@post_processing.append
def post_proc(tree, captured_registry, gen_sym, **kw):
    if captured_registry == []:
        return tree

    unpickle_name = gen_sym()
    pickle_import = [
        ImportFrom(module='pickle', names=[alias(name='loads', asname=unpickle_name)], level=0)
    ]

    import pickle

    syms = [Name(id=sym) for val, sym in captured_registry]
    vals = [val for val, sym in captured_registry]

    with q as stored:
        ast_list[syms] = name[unpickle_name](u[pickle.dumps(vals)])

    from misc import ast_ctx_fixer
    stored = ast_ctx_fixer.recurse(stored)

    tree.body = map(fix_missing_locations, pickle_import + stored) + tree.body

    return tree

@filters.append
def filter(tree, captured_registry, gen_sym, **kw):

    return fill_hygienes(tree, captured_registry, gen_sym)


@macros.block
def hq(tree, target, **kw):
    tree = unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = ast_repr(tree)

    return [Assign([target], tree)]


@macros.expr
def hq(tree, **kw):
    tree = unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = ast_repr(tree)
    return tree


@Walker
def hygienator(tree, stop, **kw):
    if type(tree) is Name and type(tree.ctx) is Load:
        stop()

        return Captured(
            tree,
            tree.id
        )

    if type(tree) is Literal:
        stop()
        return tree

    res = check_annotated(tree)
    if res:
        id, subtree = res
        if 'unhygienic' == id:
            stop()
            tree.slice.value.ctx = None
            return tree.slice.value
