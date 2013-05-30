from macropy.core import *
from macropy.core.util import *
from ast import *


# stops the traversal
stop = object()

class set_ctx(object):
    """Returned from the Walker function to set the `ctx` used when traversing
    child nodes."""
    def __init__(self, ctx):
        self.ctx = ctx

class collect(object):
    """Returned from the Walker function to collect some value during the
    traversal. A list of values collected is returned from the traveral
    by the `recurse_real` method."""
    def __init__(self, ctx):
        self.ctx = ctx

class Walker(object):
    """
    Decorates a function of the form:

    @Walker
    def transform(tree, ctx):
        ...
        return new_tree
        return new_tree, set_ctx(new_ctx), collect(value), stop

    Which is used via:

    new_tree = transform.recurse(old_tree, initial_ctx)
    new_tree = transform.recurse(old_tree)
    new_tree, collected = transform.recurse_real(old_tree, initial_ctx)
    new_tree, collected = transform.recurse_real(old_tree)

    The `transform` function takes either:

    - the `tree` to be transformed, or
    - the `tree` to be transformed and a `ctx` variable

    The `transform` function can return:

    - a single `new_tree`, which is the new AST to replace the original
    - a tuple which contains:
        - a `new_tree` AST, as above
        - `set_ctx(new_ctx)`, which causes the recursion on all child nodes to receive
          the new_ctx
        - `collect(value)`, which adds `value` to the list of collected values
          returned by `recurse_real`
        - `stop`, which prevents recursion on the children of the current tree

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

            aggregates = []
            new_tree = []
            for t in tree:
                new_t, new_a = self.recurse_real(t, ctx)
                if type(new_t) is list:
                    new_tree.extend(new_t)
                else:
                    new_tree.append(new_t)
                aggregates.extend(new_a)

            tree[:] = new_tree
            return aggregates

        else:
            return []

    def recurse(self, tree, ctx=None):
        """Traverse the given AST and return the transformed tree."""
        return self.recurse_real(tree, ctx)[0]

    def recurse_real(self, tree, ctx=None):
        """Traverse the given AST and return the transformed tree together
        with any values which were collected along with way."""
        if isinstance(tree, AST):
            aggregates = []
            stop_now = False

            # Be loose enough to work whether the function takes 1 or 2 args,
            # and whether it returns a tuple or a single tree. The types should
            # still be sound, since the various possibilities are all disjoint.
            gen = self.func(tree=tree, ctx=ctx)

            if gen is None:
                gen = ()
            if type(gen) is not tuple:
                gen = (gen,)

            for x in gen:
                if x is stop:
                    stop_now = True
                elif isinstance(x, set_ctx):
                    ctx = x.ctx
                elif isinstance(x, collect):
                    aggregates.append(x.ctx)
                else:
                    tree = x

            if not stop_now:
                aggregates.extend(self.walk_children(tree, ctx))

        else:
            aggregates = self.walk_children(tree, ctx)

        return tree, aggregates


