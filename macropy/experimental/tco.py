import ast

import macropy.core.macros
import macropy.core.util
import macropy.core.walkers

from macropy.core import Captured
from macropy.experimental.pattern import macros, switch, _matching, ClassMatcher, NameMatcher

from macropy.core.hquotes import macros, hq

__all__ = ['tco']

macros = macropy.core.macros.Macros()

in_tc_stack = [False]

@macropy.core.util.singleton
class TcoIgnore:
    pass

@macropy.core.util.singleton
class TcoCall:
    pass


def trampoline(func, args, kwargs):
    """
    Repeatedly apply a function until it returns a value.

    The function may return (tco.CALL, func, args, kwargs) or (tco.IGNORE,
    func, args, kwargs) or just a value.
    """
    ignoring = False
    while True:
        # We can only set this if we know it will be immediately unset by func
        if hasattr(func, 'tco'):
            in_tc_stack[0] = True
        result = func(*args, **kwargs)
        # for performance reasons, do not use pattern matching here
        if isinstance(result, tuple):
            if result[0] is TcoCall:
                func = result[1]
                args = result[2]
                kwargs = result[3]
                continue
            elif result[0] is TcoIgnore:
                ignoring = True
                func = result[1]
                args = result[2]
                kwargs = result[3]
                continue
        if ignoring:
            return None
        else:
            return result



def trampoline_decorator(func):
    import functools
    @functools.wraps(func)
    def trampolined(*args, **kwargs):
        if in_tc_stack[0]:
            in_tc_stack[0] = False
            return func(*args, **kwargs)
        in_tc_stack.append(False)
        return trampoline(func, args, kwargs)

    trampolined.tco = True
    return trampolined


@macros.decorator
def tco(tree, **kw):

    @macropy.core.walkers.Walker
    # Replace returns of calls
    def return_replacer(tree, **kw):
        with switch(tree):
            if ast.Return(value=ast.Call(
                    func=func, 
                    args=args, 
                    starargs=starargs, 
                    kwargs=kwargs)):
                if starargs:
                    with hq as code:
                    # get rid of starargs
                        return (TcoCall,
                                ast_literal[func],
                                ast_literal[ast.List(args, ast.Load())] + list(ast_literal[starargs]),
                                ast_literal[kwargs or ast.Dict([],[])])
                else:
                    with hq as code:
                        return (TcoCall,
                                ast_literal[func],
                                ast_literal[ast.List(args, ast.Load())],
                                ast_literal[kwargs or ast.Dict([], [])])

                return code
            else:
                return tree

    # Replace calls (that aren't returned) which happen to be in a tail-call
    # position
    def replace_tc_pos(node):
        with switch(node):
            if ast.Expr(value=ast.Call(
                    func=func,
                    args=args,
                    starargs=starargs,
                    kwargs=kwargs)):
                if starargs:
                    with hq as code:
                    # get rid of starargs
                        return (TcoIgnore,
                                ast_literal[func],
                                ast_literal[ast.List(args, ast.Load())] + list(ast_literal[starargs]),
                                ast_literal[kwargs or ast.Dict([],[])])
                else:
                    with hq as code:
                        return (TcoIgnore,
                                ast_literal[func],
                                ast_literal[ast.List(args, ast.Load())],
                                ast_literal[kwargs or ast.Dict([], [])])
                return code
            elif ast.If(test=test, body=body, orelse=orelse):
                body[-1] = replace_tc_pos(body[-1])
                if orelse:
                    orelse[-1] = replace_tc_pos(orelse[-1])
                return ast.If(test, body, orelse)
            else:
                return node

    tree = return_replacer.recurse(tree)

    tree.decorator_list = ([hq[trampoline_decorator]] +
            tree.decorator_list)

    tree.body[-1] = replace_tc_pos(tree.body[-1])

    return tree
