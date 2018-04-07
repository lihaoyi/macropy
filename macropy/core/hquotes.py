# -*- coding: utf-8 -*-
"""Hygienic Quasiquotes, which pull in names from their definition
scope rather than their expansion scope.
"""

import ast
import pickle

from .macros import (Macros, check_annotated, filters, injected_vars,
                     macro_stub, post_processing)

from .quotes import (macros, q, unquote_search, u, ast_list,   # noqa: F401
                     name, ast_literal)
from .analysis import Scoped

from . import ast_repr, Captured, Literal
from .util import register
from .walkers import Walker


# Monkey Patching pickle to pickle module objects properly See if
# there is a way to do a better job with the dispatch tables, in the
# meantime the code in post_proc() will use non-accelerated
# pickler/unpickler.
pickle._Pickler.dispatch[type(pickle)] = pickle._Pickler.save_global


macros = Macros()  # noqa F811


@macro_stub
def unhygienic():
    """Used to delimit a section of a hq[...] that should not be
    hygienified."""


@register(injected_vars)
def captured_registry(**kw):
    return []


@register(post_processing)  # noqa: F811
def post_proc(tree, captured_registry, gen_sym, **kw):
    if len(captured_registry) == 0:
        return tree

    unpickle_name = gen_sym("unpickled")
    with q as pickle_import:
        from pickle import _loads as x  # noqa: F401

    pickle_import[0].names[0].asname = unpickle_name

    import pickle

    syms = [ast.Name(id=sym) for val, sym in captured_registry]
    vals = [val for val, sym in captured_registry]

    with q as stored:
        ast_list[syms] = name[unpickle_name](u[pickle._dumps(vals)])

    from .cleanup import ast_ctx_fixer
    stored = ast_ctx_fixer.recurse(stored)

    tree.body = (list(map(ast.fix_missing_locations, pickle_import + stored)) +
                 tree.body)

    return tree


@register(filters)
def hygienate(tree, captured_registry, gen_sym, **kw):
    # print('Hygienate %s' % ast.dump(tree) if isinstance(tree, ast.AST)
    #       else tree, file=sys.stderr)
    @Walker
    def hygienator(tree, stop, **kw):
        if type(tree) is Captured:
            new_sym = [sym for val, sym in captured_registry
                       if val is tree.val]
            if not new_sym:
                new_sym = gen_sym(tree.name)
                captured_registry.append((tree.val, new_sym))
            else:
                new_sym = new_sym[0]
            return ast.Name(new_sym, ast.Load())

    return hygienator.recurse(tree)


@macros.block
def hq(tree, target, **kw):
    tree = unquote_search.recurse(tree)
    tree = hygienator.recurse(tree)
    tree = ast_repr(tree)
    # print('Hquote block %s' % ast.dump(tree) if isinstance(tree, ast.AST)
    #       else tree, file=sys.stderr)
    return [ast.Assign([target], tree)]


@macros.expr  # noqa: F811
def hq(tree, **kw):
    """Hygienic Quasiquote macro, used to quote sections of code while
    ensuring that names within the quoted code will refer to the value
    bound to that name when the code was quoted. Used together with
    the `u`, `name`, `ast`, `ast_list`, `unhygienic` unquotes.
    """
    tree = unquote_search.recurse(tree)
    # print('Hquote after search %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    tree = hygienator.recurse(tree)
    # print('Hquote after hygienator %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    tree = ast_repr(tree)
    # print('Hquote after repr %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    return tree


@Scoped
@Walker
def hygienator(tree, stop, scope, **kw):
    if (type(tree) is ast.Name and type(tree.ctx) is ast.Load and
        tree.id not in scope.keys()):  # noqa E129
        stop()
        return Captured(tree, tree.id)

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


macros.expose_unhygienic(ast)
macros.expose_unhygienic(ast_repr)
macros.expose_unhygienic(Captured)
macros.expose_unhygienic(Literal)
