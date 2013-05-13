# import pattern matching
# import quoting / unquoting
from macropy.macros.pattern import macros
from macropy.macros.pattern import *
from macropy.core.lift import macros
from macropy.core.lift import *
from ast import *

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
        result = func(*(args + varargs), **kwargs)
        with switch(result):
            if ('call', func, args, varargs, kwargs):
                pass
            elif ('ignore', func, args, varargs, kwargs):
                ignoring = True
            else:
                pass # break out of switch >.<
                if ignoring:
                    _exit_trampoline()
                    return None
                else:
                    _exit_trampoline()
                    return result


@macros.decorator()
def tco(node):

    @Walker
    # Replace returns of calls - TODO use pattern matching here
    def return_replacer(node):
        if isinstance(node, Return): 
            if isinstance(node.value, Call):
                with q as code:
                    return ('call', ast%(node.value.func),
                            ast%(List(node.value.args, Load())),
                            ast%(node.value.starargs or List([], Load())),
                            ast%(node.value.kwargs or Dict([],[])))
                return code
# TODO this is a stupid hack - should actually just not recurse once a return
# statement has been replaced.
            else:
                return node
        return node

    # Replace calls (that aren't returned) which happen to be in a tail-call
    # position
    def replace_tc_pos(node):
        if isinstance(node, Expr) and isinstance(node.value, Call):
            with q as code:
                return ('ignore', ast%(node.value.func), 
                        ast%(List(node.value.args, Load())),
                        ast%(node.value.starargs or List([], Load())),
                        ast%(node.value.kwargs or Dict([], [])))
            return code
        elif isinstance(node, If):
            node.body[-1] = replace_tc_pos(node.body[-1])
            if node.orelse:
                node.orelse[-1] = replace_tc_pos(node.orelse[-1])
            return node
        return node

    # We need to remove ourselves from the decorator list so we don't have
    # infinite expansion
    new_decorator_list = []
    for decorator in node.decorator_list:
        if not (isinstance(decorator, Name) and decorator.id == 'tco'):
            new_decorator_list.append(decorator)
    node.decorator_list = new_decorator_list

    arg_list_node = List(node.args.args, Load())
    for x in arg_list_node.elts:
        assert isinstance(x, Name)
        x.ctx = Load()

    with q as prelude:
        if not in_trampoline():
            return trampoline(name%(node.name), ast%(arg_list_node), [], {})

    node = return_replacer.recurse(node)
    node.body = [prelude] + node.body
    node.body[-1] = replace_tc_pos(node.body[-1])
    return node
