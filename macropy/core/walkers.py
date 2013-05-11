from macropy.core import *
from macropy.core.util import *
from ast import *


stop = object()


class GenericWalker(object):
    """
    Decorates a function of the form

    @GenericWalker
    def transform(tree, ctx):
        ...
        return new_tree, new_ctx, aggregate

    new_tree, all_aggregates = transform.recurse(old_tree, initial_ctx)

    Where `aggregate` is a `list` of 0 or more elements, which will be
    aggregated into one final list (`all_aggregates`) when recurse returns.
    `new_ctx` is an arbitrary value which is passed down from a tree to its
    children automatically by the recursion, who will receive it in the `ctx`
    parameter when they are recursed upon.

    The decorated function can also terminate the recursion by returning the
    singleton value `stop` as `new_ctx`.
    """
    def __init__(self, func):
        self.func = func
        #self.flatten = lambda mylist: [l for sub in mylist for l in sub]

    def walk_children(self, tree, ctx=None):
        if isinstance(tree, AST):
            aggregates = []
            for field, old_value in iter_fields(tree):
                old_value = getattr(tree, field, None)
                new_value, new_aggregate = self.recurse_real(old_value, ctx)
                aggregates.extend(new_aggregate)

                setattr(tree, field, new_value)
            return aggregates
        elif isinstance(tree, list) and len(tree) > 0:
            x = zip(*map(lambda x: self.recurse_real(x, ctx), tree))
            [trees, aggregates] = x
            tree[:] = flatten(trees)
            return [x for y in aggregates for x in y]
        else:
            return []

    def recurse(self, tree, ctx=None):
        return self.recurse_real(tree, ctx)

    def recurse_real(self, tree, ctx=None):
        if ctx is stop:
            return tree, []
        else:
            x = self.func(tree, ctx)
            if x is not None :
                tree, new_ctx, aggregate = x
                assert type(aggregate) is list
                aggregates = self.walk_children(tree, new_ctx)

                return tree, aggregate + aggregates
            else:
                return tree, []


class AggregateWalker(GenericWalker):
    """
    Decorates a function of the form

    @AggregateWalker
    def transform(tree):
        ...
        return new_tree, aggregate

    new_tree, all_aggregates = transform.recurse(old_tree)

    Where `aggregate` is a `list` of 0 or more elements, which will be
    aggregated into one final list (`all_aggregates`) when recurse returns.
    """
    def __init__(self, func):
        self.func = lambda tree, ctx: (lambda x: (x[0], [], x[1]))(func(tree))

    def recurse(self, tree):
        return self.recurse_real(tree)


class ContextWalker(GenericWalker):
    """
    Decorates a function of the form

    @ContextWalker
    def transform(tree, ctx):
        ...
        return new_tree, new_ctx

    new_tree = transform.recurse(old_tree, initial_context)

    Where `new_ctx` is an arbitrary value which is passed down from a tree to its
    children automatically by the recursion, who will receive it in the `ctx`
    parameter when they are recursed upon.

    The decorated function can also terminate the recursion by returning the
    singleton value `stop` as `new_ctx`.

    """
    def __init__(self, func):
        self.func = lambda tree, ctx: (lambda x: (x[0], x[1], []))(func(tree, ctx))

    def recurse(self, tree, ctx):
        return self.recurse_real(tree, ctx)[0]


class Walker(GenericWalker):
    """
    Decorates a function of the form

    @Walker
    def transform(tree):
        ...
        return new_tree

    new_tree = transform.recurse(old_tree)
    """
    def __init__(self, func):
        self.func = lambda tree, ctx: (func(tree), [], [])

    def recurse(self, tree):
        res, agg = self.recurse_real(tree)
        return res
