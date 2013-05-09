# import pattern matching
# import quoting / unquoting
from macropy.macros.pattern import macros
from macropy.macros.pattern import *
from macropy.core.lift import macros
from macropy.core.lift import *
from ast import *

# stupid read-only closures
_in_trampoline = [False]

def _enter_trampoline():
    _in_trampoline[0] = True

def _exit_trampoline():
    _in_trampoline[0] = False

def in_trampoline():
    return _in_trampoline[0]

def trampoline(func, args):
    """
    Repeatedly apply a function until it returns a value.

    The function may return ('call', func, args) or ('ignore', func,
    args) or ('return', val)
    """
    _enter_trampoline()
    ignoring = False
    while True:
        result = func(*args)
        with switch(result[0]):
            if 'call':
                (func, args) = (result[1], result[2])
            elif 'ignore':
                (func, args) = (result[1], result[2])
                ignoring = True
            elif 'return':
                if ignoring:
                    _exit_trampoline()
                    return None
                else:
                    _exit_trampoline()
                    return result[1]

@macros.decorator
def tco(node):
    @Walker
    def func(node):
        if isinstance(node, Return): 
            if isinstance(node.value, Call):
                with q as code:
                    return ('call', ast%(node.value.func),
                            ast%(List(node.value.args, Load())))
                return code
            elif not (isinstance(node.value, Tuple)
                    and isinstance(node.value.elts[0], Str)
                    and node.value.elts[0].s in ['return', 'call']):
                with q as code:
                    return ('return', ast%(node.value))
                return code
            else:
                return node
        else:
            return node
    new_decorator_list = []
    for decorator in node.decorator_list:
        if not (isinstance(decorator, Name) and decorator.id == 'tco'):
            new_decorator_list.append(decorator)

    arg_list_node = List(node.args.args, Load())
    for x in arg_list_node.elts:
        assert isinstance(x, Name)
        x.ctx = Load()

    with q as prelude:
        if not in_trampoline():
            return trampoline(name%(node.name), ast%(arg_list_node))

    node.decorator_list = new_decorator_list
    node = func.recurse(node)
    node.body = [prelude] + node.body
    return node
