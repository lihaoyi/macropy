# import pattern matching
# import quoting / unquoting
from macropy.core.macros import *
from macropy.macros.pattern import macros, switch, _matching

from macropy.core.lift import macros, q

macros = Macros()

# stupid read-only closures
_in_trampoline = [False]


def _enter_trampoline():
    _in_trampoline[0] = True


def _exit_trampoline():
    _in_trampoline[0] = False


def in_trampoline():
    return _in_trampoline[0]


def trampoline(func, args, varargs, kwargs):
    """
    Repeatedly apply a function until it returns a value.

    The function may return ('call', func, args, varargs, kwargs) or ('ignore', func, args) or ('return', val)
    """
    _enter_trampoline()
    ignoring = False
    while True:
        result = func(*(list(args) + varargs), **kwargs)
        with switch(result):
            if ('macropy-tco-call', func, args, varargs, kwargs):
                pass
            elif ('macropy-tco-ignore', func, args, varargs, kwargs):
                ignoring = True
            else:
                pass # break out of switch >.<
                if ignoring:
                    _exit_trampoline()
                    return None
                else:
                    _exit_trampoline()
                    return result


def trampoline_decorator(func):
    import functools
    @functools.wraps(func)
    def trampolined(*args, **kwargs):
        if not in_trampoline():
            return trampoline(func, args, [], kwargs)
        return func(*args, **kwargs)
    return trampolined


@macros.decorator()
def tco(tree, **kw):
    @Walker
    # Replace returns of calls - TODO use pattern matching here
    def return_replacer(tree, **kw):
        if isinstance(tree, Return):
            if isinstance(tree.value, Call):
                with q as code:
                    return ('macropy-tco-call',
                            ast(tree.value.func),
                            ast(List(tree.value.args, Load())),
                            ast(tree.value.starargs or List([], Load())),
                            ast(tree.value.kwargs or Dict([],[])))
                return code
            else:
                return tree
        return tree

    # Replace calls (that aren't returned) which happen to be in a tail-call
    # position
    def replace_tc_pos(node):
        if isinstance(node, Expr) and isinstance(node.value, Call):
            with q as code:
                return ('macropy-tco-ignore',
                        ast(node.value.func),
                        ast(List(node.value.args, Load())),
                        ast(node.value.starargs or List([], Load())),
                        ast(node.value.kwargs or Dict([], [])))
            return code
        elif isinstance(node, If):
            node.body[-1] = replace_tc_pos(node.body[-1])
            if node.orelse:
                node.orelse[-1] = replace_tc_pos(node.orelse[-1])
            return node
        return node

    # We need to remove ourselves from the decorator list so we don't have
    # infinite expansion

    arg_list_node = List(tree.args.args, Load())
    for x in arg_list_node.elts:
        assert isinstance(x, Name)
        x.ctx = Load()

    tree = return_replacer.recurse(tree)
    tree.decorator_list = ([q(tco.trampoline_decorator)] +
            tree.decorator_list)
    tree.body[-1] = replace_tc_pos(tree.body[-1])
    return tree


# ok, so now you will only need to import tco...
tco.trampoline_decorator = trampoline_decorator
