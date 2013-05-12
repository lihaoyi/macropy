from macropy.core import *
from macropy.core.util import *
from ast import *


stop = object()

class set_ctx(object):
    def __init__(self, ctx):
        self.ctx = ctx

class collect(object):
    def __init__(self, ctx):
        self.ctx = ctx

class Walker(object):
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
        return self.recurse_real(tree, ctx)[0]

    def recurse_real(self, tree, ctx=None):
        if isinstance(tree, AST):
            func_aggregates = []
            stop_now = False
            try:
                gen = self.func(tree, ctx)
            except:
                gen = self.func(tree)

            for x in gen:
                if x is stop:
                    stop_now = True
                elif isinstance(x, set_ctx):
                    ctx = x.ctx
                elif isinstance(x, collect):
                    func_aggregates.append(x.ctx)
                else:
                    tree = x
            if stop_now:
                return tree, func_aggregates
            else:
                aggregates = self.walk_children(tree, ctx)
                return tree, func_aggregates + aggregates
        else:
            aggregates = self.walk_children(tree, ctx)
            return tree, aggregates


