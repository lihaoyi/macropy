import ast
import enum
import functools

from ..core import Captured  # noqa: F401
from ..core.hquotes import macros, hq  # noqa: F811
from ..core.macros import Macros
from ..core.walkers import Walker
from ..core.compat import PY35

if not PY35:
    raise RuntimeError("Tail-call optimization works only on Py3.5+ for now.")

from .pattern import (  # noqa: F401,F811
    macros, switch, ClassMatcher, NameMatcher)


macros = Macros()  # noqa: F811

in_tc_stack = [False]

TCOType = enum.Enum('TCOType', ('IGNORE', 'CALL'))


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
            if result[0] is TCOType.CALL:
                func = result[1]
                args = result[2]
                kwargs = result[3]
                continue
            elif result[0] is TCOType.IGNORE:
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

    @Walker
    # Replace returns of calls
    def return_replacer(tree, **kw):
        with switch(tree):
            if ast.Return(value=ast.Call(
                    func=func,
                    args=args,
                    keywords=keywords)):
                starred = [arg for arg in args if isinstance(arg, ast.Starred)]
                kwargs = [kw for kw in keywords if kw.arg is None]

                if len(kwargs):
                    kwargs = kwargs[0].value
                if len(starred):
                    starred = starred[0].value
                    with hq as code:
                    # get rid of starargs
                        return (TCOType.CALL,
                                ast_literal[func],
                                (ast_literal[ast.List(args, ast.Load())] +
                                 list(ast_literal[starred])),
                                ast_literal[kwargs or ast.Dict([],[])])
                else:
                    with hq as code:
                        return (TCOType.CALL,
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
                    keywords=keywords)):
                starred = [arg for arg in args if isinstance(arg, ast.Starred)]
                kwargs = [kw for kw in keywords if kw.arg is None]

                if len(kwargs):
                    kwargs = kwargs[0].value
                if len(starred):
                    starred = starred[0].value
                    with hq as code:
                    # get rid of starargs
                        return (TCOType.IGNORE,
                                ast_literal[func],
                                (ast_literal[ast.List(args, ast.Load())] +
                                 list(ast_literal[starred])),
                                ast_literal[kwargs or ast.Dict([],[])])
                else:
                    with hq as code:
                        return (TCOType.IGNORE,
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
