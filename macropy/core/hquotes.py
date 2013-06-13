"""Hygienic Quasiquotes, which pull in names from their definition scope rather
than their expansion scope."""
from macropy.core.macros import *

from macropy.core.quotes import macros, q, unquote_search, u, ast, ast_list, name


macros = Macros()

@singleton
class unhygienic():
    """Used to delimit a section of a hq[...] that should not be hygienified"""


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
