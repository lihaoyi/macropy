"""Hygienic Quasiquotes, which pull in names from their definition scope rather
than their expansion scope."""
from macropy.core.macros import *

from macropy.core.quotes import macros, q, unquote_search, u, ast, ast_list, name
from macropy.core.analysis import Scoped

macros = Macros()

@macro_stub
def unhygienic():
    """Used to delimit a section of a hq[...] that should not be hygienified"""

from .macros import filters, injected_vars, post_processing

@register(injected_vars)
def captured_registry(**kw):
    return []

@register(post_processing)
def post_proc(tree, captured_registry, gen_sym, **kw):
    if captured_registry == []:
        return tree

    unpickle_name = gen_sym("unpickled")
    with q as pickle_import:
        from pickle import loads as x

    pickle_import[0].names[0].asname = unpickle_name

    import pickle

    syms = [Name(id=sym) for val, sym in captured_registry]
    vals = [val for val, sym in captured_registry]

    with q as stored:
        ast_list[syms] = name[unpickle_name](u[pickle.dumps(vals)])

    from .cleanup import ast_ctx_fixer
    stored = ast_ctx_fixer.recurse(stored)

    tree.body = list(map(fix_missing_locations, pickle_import + stored)) + tree.body

    return tree

@register(filters)
def hygienate(tree, captured_registry, gen_sym, **kw):
    @Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is Captured:
            new_sym = [sym for val, sym in captured_registry if val is tree.val]
            if not new_sym:
                new_sym = gen_sym(tree.name)

                captured_registry.append((tree.val, new_sym))
            else:
                new_sym = new_sym[0]
            return Name(new_sym, Load())

    return hygienator.recurse(tree)


@macros.block
def hq(tree, target, **kw):
    tree = unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = ast_repr(tree)

    return [Assign([target], tree)]


@macros.expr
def hq(tree, **kw):
    """Hygienic Quasiquote macro, used to quote sections of code while ensuring
    that names within the quoted code will refer to the value bound to that name
    when the code was quoted. Used together with the `u`, `name`, `ast`,
    `ast_list`, `unhygienic` unquotes."""
    tree = unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = ast_repr(tree)
    return tree


@Scoped
@Walker
def hygienator(tree, stop, scope, **kw):
    if type(tree) is Name and \
            type(tree.ctx) is Load and \
            tree.id not in scope.keys():

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

