# -*- coding: utf-8 -*-
"""Implementation of Walkers, a nice way of transforming and
traversing ASTs."""

import ast

from . import Captured, Literal


class Walker(object):
    """@Walker decorates a function of the form:

    @Walker
    def transform(tree, **kw):
        ...
        return new_tree


    Which is used via:

    new_tree = transform.recurse(old_tree, initial_ctx)
    new_tree = transform.recurse(old_tree)
    new_tree, collected = transform.recurse_collect(old_tree, initial_ctx)
    new_tree, collected = transform.recurse_collect(old_tree)
    collected = transform.collect(old_tree, initial_ctx)
    collected = transform.collect(old_tree)

    The `transform` function takes the tree to be transformed, in addition to
    a set of `**kw` which provides additional functionality:


    - `set_ctx`: this is a function, used via `set_ctx(name=value)`
      anywhere in `transform`, which will cause any children of `tree`
      to receive `name` as an argument with a value `value.
    - `set_ctx_for`: this is similar to `set_ctx`, but takes an
      additional parameter `tree` (i.e. `set_ctx_for(tree,
      name=value)`) and `name` is only injected into the parameter
      list of `transform` when `tree` is the AST snippet being
      transformed.
    - `collect`: this is a function used via `collect(thing)`, which
      adds `thing` to the `collected` list returned by
      `recurse_collect`.
    - `stop`: when called via `stop()`, this prevents recursion on
      children of the current tree.

    These additional arguments can be declared in the signature, e.g.:

    @Walker
    def transform(tree, ctx, set_ctx, **kw):
        ... do stuff with ctx ...
        set_ctx(...)
        return new_tree

    for ease of use.

    """
    def __init__(self, func):
        self.func = func

    def walk_children(self, tree, sub_kw=[], **kw):
        if isinstance(tree, ast.AST):
            aggregates = []

            for field, old_value in ast.iter_fields(tree):

                old_value = getattr(tree, field, None)
                specific_sub_kw = [
                    (k, v)
                    for item, kws in sub_kw
                    if item is old_value
                    for k, v in kws.items()
                ]
                new_value, new_aggregate = self.recurse_collect(
                    old_value, sub_kw,
                    **dict(list(kw.items()) + specific_sub_kw))
                aggregates.extend(new_aggregate)
                setattr(tree, field, new_value)

            return aggregates

        elif isinstance(tree, list) and len(tree) > 0:
            aggregates = []
            new_tree = []

            for t in tree:
                new_t, new_a = self.recurse_collect(t, sub_kw, **kw)
                if type(new_t) is list:
                    new_tree.extend(new_t)
                else:
                    new_tree.append(new_t)
                aggregates.extend(new_a)

            tree[:] = new_tree
            return aggregates

        else:
            return []

    def recurse(self, tree, **kw):
        """Traverse the given AST and return the transformed tree."""
        return self.recurse_collect(tree, **kw)[0]

    def collect(self, tree, **kw):
        """Traverse the given AST and return the transformed tree."""
        return self.recurse_collect(tree, **kw)[1]

    def recurse_collect(self, tree, sub_kw=[], **kw):
        """Traverse the given AST and return the transformed tree together
        with any values which were collected along with way."""

        if (isinstance(tree, ast.AST) or type(tree) is Literal or
            type(tree) is Captured):  # noqa: #E129
            aggregates = []
            stop_now = [False]

            def stop():
                stop_now[0] = True

            new_ctx = dict(**kw)
            new_ctx_for = sub_kw[:]

            def set_ctx(**new_kw):
                new_ctx.update(new_kw)

            def set_ctx_for(tree, **kw):
                new_ctx_for.append((tree, kw))

            # Provide the function with a bunch of controls, in addition to
            # the tree itself.
            new_tree = self.func(
                tree=tree,
                collect=aggregates.append,
                set_ctx=set_ctx,
                set_ctx_for=set_ctx_for,
                stop=stop,
                **kw
            )

            if new_tree is not None:
                tree = new_tree

            if not stop_now[0]:
                aggregates.extend(self.walk_children(tree, new_ctx_for,
                                                     **new_ctx))

        else:
            aggregates = self.walk_children(tree, sub_kw, **kw)

        return tree, aggregates
