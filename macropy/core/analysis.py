# -*- coding: utf-8 -*-
"""Walker that performs simple name-binding analysis as it traverses the AST"""

import ast

from .util import merge_dicts
from .walkers import Walker
from . import compat


__all__ = ['Scoped']


@Walker
def find_names(tree, collect, stop, **kw):
    if isinstance(tree, (ast.Attribute, ast.Subscript)):
        stop()
    if isinstance(tree, ast.Name):
        collect((tree.id, tree))


@Walker
def find_assignments(tree, collect, stop, **kw):
    if isinstance(tree, compat.scope_nodes):
        collect((tree.name, tree))
        stop()
    if isinstance(tree, ast.Assign):
        for x in find_names.collect(tree.targets):
            collect(x)


def extract_arg_names(args):
    return dict(
        ([(args.vararg.arg, args.vararg)] if args.vararg else []) +
        ([(args.kwarg.arg, args.kwarg)] if args.kwarg else []) +
        [(arg.arg, arg) for arg in args.args] +
        [(arg.arg, arg) for arg in args.kwonlyargs]
    )


class Scoped(Walker):
    """Used in conjunction with `@Walker`, via

    @Scoped
    @Walker
    def my_func(tree, scope, **kw):
        ...

    This decorator wraps the `Walker` and injects in a `scope` argument into
    the function. This argument is a dictionary of names which are in-scope
    in the present `tree`s environment, starting from the `tree` on which the
    recursion was start.

    This can be used to track the usage of a name binding through the AST
    snippet, and detecting when the name gets shadowed by a more tightly scoped
    name binding.
    """

    def __init__(self, walker):
        self.walker = walker

    def recurse_collect(self, tree, sub_kw=[], **kw):

        kw['scope'] = kw.get('scope', dict(find_assignments.collect(tree)))
        return Walker.recurse_collect(self, tree, sub_kw, **kw)

    def func(self, tree, set_ctx_for, scope, **kw):

        def extend_scope(tree, *dicts, **kw):
            new_scope = merge_dicts(*([scope] + list(dicts)))
            if "remove" in kw:
                for rem in kw['remove']:
                    del new_scope[rem]

            set_ctx_for(tree, scope=new_scope)
        if isinstance(tree, ast.Lambda):
            extend_scope(tree.body, extract_arg_names(tree.args))

        if isinstance(tree, (ast.GeneratorExp, ast.ListComp, ast.SetComp,
                             ast.DictComp)):
            iterator_vars = {}
            for gen in tree.generators:
                extend_scope(gen.target, iterator_vars)
                extend_scope(gen.iter, iterator_vars)
                iterator_vars.update(dict(find_names.collect(gen.target)))
                extend_scope(gen.ifs, iterator_vars)

            if isinstance(tree, ast.DictComp):
                extend_scope(tree.key, iterator_vars)
                extend_scope(tree.value, iterator_vars)
            else:
                extend_scope(tree.elt, iterator_vars)

        if isinstance(tree, compat.function_nodes):

            extend_scope(tree.args, {tree.name: tree})
            extend_scope(
                tree.body,
                {tree.name: tree},
                extract_arg_names(tree.args),
                dict(find_assignments.collect(tree.body)),
            )

        if isinstance(tree, ast.ClassDef):
            extend_scope(tree.bases, remove=[tree.name])
            extend_scope(tree.body, dict(find_assignments.collect(tree.body)),
                         remove=[tree.name])

        if isinstance(tree, ast.ExceptHandler):
            extend_scope(tree.body, {tree.name: tree.name})

        if isinstance(tree, ast.For):
            extend_scope(tree.body, dict(find_names.collect(tree.target)))

        if isinstance(tree, ast.With):
            extend_scope(tree.body, dict(find_names.collect(tree.items)))

        return self.walker.func(
            tree,
            set_ctx_for=set_ctx_for,
            scope=scope,
            **kw
        )
