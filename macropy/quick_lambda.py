# -*- coding: utf-8 -*-
import ast

from .core.macros import Macros, injected_vars, post_processing
from .core.util import Lazy, register
from .core.quotes import macros, name, q, ast_literal, u
from .core.hquotes import macros, hq, u  # noqa: F811
from .core.cleanup import ast_ctx_fixer
from .core import ast_repr, Captured  # noqa: F401
from .core.walkers import Walker


macros = Macros()  # noqa: F811


def _():
    """Placeholder for a function argument in the `f` macro."""


@macros.expr  # noqa: F811
def f(tree, gen_sym, **kw):
    """Macro to concisely create function literals; any `_`s within the
    wrapped expression becomes an argument to the generated function."""
    @Walker
    def underscore_search(tree, collect, **kw):
        if isinstance(tree, ast.Name) and tree.id == "_":
            name = gen_sym("_")
            tree.id = name
            collect(name)
            return tree

    tree, used_names = underscore_search.recurse_collect(tree)

    new_tree = q[lambda: ast_literal[tree]]
    new_tree.args.args = [ast.arg(arg=x) for x in used_names]
    return new_tree


@macros.expr
def lazy(tree, **kw):
    """Macro to wrap an expression in a lazy memoizing thunk. This can be
    called via `thing()` to extract the value. The wrapped expression is
    only evaluated the first time the thunk is called and the result cached
    for all subsequent evaluations."""
    return hq[Lazy(lambda: ast_literal[tree])]


def get_interned(store, index, thunk):
    if store[index] is None:
        store[index] = [thunk()]
    return store[index][0]


@register(injected_vars)
def interned_count(**kw):
    return [0]


@register(injected_vars)  # noqa: F811
def interned_name(gen_sym, **kw):
    return gen_sym()


@register(post_processing)  # noqa: F811
def interned_processing(tree, gen_sym, interned_count, interned_name, **kw):

    if interned_count[0] != 0:
        with q as code:
            name[interned_name] = [None for x in range(u[interned_count[0]])]

        code = ast_ctx_fixer.recurse(code)
        code = list(map(ast.fix_missing_locations, code))

        tree.body = code + tree.body

    return tree


@macros.expr
def interned(tree, interned_name, interned_count, **kw):
    """Macro to intern the wrapped expression on a per-module basis"""
    interned_count[0] += 1

    hq[name[interned_name]]

    return hq[get_interned(name[interned_name], interned_count[0] - 1, lambda: ast_literal[tree])]
