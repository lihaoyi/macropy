# -*- coding: utf-8 -*-
import ast
import copy

import macropy.core
import macropy.core.macros
import macropy.core.walkers

from macropy.core.quotes import ast_literal, u
from macropy.core.hquotes import macros, hq, unhygienic


macros = macropy.core.macros.Macros()  # noqa: F811


def literal_eval(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the
    following Python literal structures: strings, numbers, tuples,
    lists, dicts, booleans, and None.
    """
    _safe_names = {'None': None, 'True': True, 'False': False}
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='eval')
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body

    def _convert(node):
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, ast.List):
            return list(map(_convert, node.elts))
        elif isinstance(node, ast.Dict):
            return dict((_convert(k), _convert(v)) for k, v
                        in zip(node.keys, node.values))
        elif isinstance(node, ast.Name):
            if node.id in _safe_names:
                return _safe_names[node.id]
        elif (isinstance(node, ast.BinOp) and
              isinstance(node.op, (ast.Add, ast.Sub)) and
              isinstance(node.right, ast.Num) and
              isinstance(node.right.n, complex) and
              isinstance(node.left, ast.Num) and
              isinstance(node.left.n, (int, float))):  # TODO: long,
            left = node.left.n
            right = node.right.n
            if isinstance(node.op, ast.Add):
                return left + right
            else:
                return left - right
        raise ValueError('malformed string')
    return _convert(node_or_string)


def wrap(printer, txt, x):
    string = txt + " -> " + repr(x)
    printer(string)
    return x


def wrap_simple(printer, txt, x):
    string = txt
    printer(string)
    return x


@macros.expr
def log(tree, exact_src, **kw):
    """Prints out source code of the wrapped expression and the value it
    evaluates to"""
    new_tree = hq[wrap(unhygienic[log], u[exact_src(tree)], ast_literal[tree])]
    yield new_tree


@macros.expr
def show_expanded(tree, expand_macros,  **kw):
    """Prints out the expanded version of the wrapped source code, after all
    macros inside it have been expanded"""
    new_tree = hq[wrap_simple(
        unhygienic[log], u[macropy.core.unparse(tree)],
        ast_literal[tree])]
    return new_tree


@macros.block   # noqa: F811
def show_expanded(tree, expand_macros, **kw):
    """Prints out the expanded version of the wrapped source code, after all
    macros inside it have been expanded"""
    new_tree = []
    for stmt in tree:
        with hq as code:
            unhygienic[log](u[macropy.core.unparse(stmt)])
        new_tree.append(code)
        new_tree.append(stmt)

    return new_tree


def trace_walk_func(tree, exact_src):
    @macropy.core.walkers.Walker
    def trace_walk(tree, stop, **kw):

        if (isinstance(tree, ast.expr) and
            tree._fields != () and
            type(tree) is not ast.Name):  # noqa: E129

            try:
                literal_eval(tree)
                stop()
                return tree
            except ValueError as e:
                txt = exact_src(tree)
                trace_walk.walk_children(tree)
                wrapped = hq[wrap(unhygienic[log], u[txt], ast_literal[tree])]
                stop()
                return wrapped

        elif isinstance(tree, ast.stmt):
            txt = exact_src(tree)
            trace_walk.walk_children(tree)
            with hq as code:
                unhygienic[log](u[txt])
            stop()
            return [code, tree]

    return trace_walk.recurse(tree)


@macros.expr
def trace(tree, exact_src, **kw):
    """Traces the wrapped code, printing out the source code and evaluated
    result of every statement and expression contained within it"""
    ret = trace_walk_func(tree, exact_src)
    yield ret


@macros.block  # noqa: F811
def trace(tree, exact_src, **kw):
    """Traces the wrapped code, printing out the source code and evaluated
    result of every statement and expression contained within it"""
    ret = trace_walk_func(tree, exact_src)
    yield ret


def require_transform(tree, exact_src):
    ret = trace_walk_func(copy.deepcopy(tree), exact_src)
    trace_walk_func(copy.deepcopy(tree), exact_src)
    new = hq[ast_literal[tree] or wrap_require(lambda log: ast_literal[ret])]
    return new


def wrap_require(thunk):
    out = []
    thunk(out.append)
    raise AssertionError("Require Failed\n" + "\n".join(out))


@macros.expr
def require(tree, exact_src, **kw):
    """A version of assert that traces the expression's evaluation in the
    case of failure. If used as a block, performs this on every expression
    within the block"""
    yield require_transform(tree, exact_src)


@macros.block  # noqa: F811
def require(tree, exact_src, **kw):
    """A version of assert that traces the expression's evaluation in the
    case of failure. If used as a block, performs this on every expression
    within the block"""
    for expr in tree:
        expr.value = require_transform(expr.value, exact_src)

    yield tree


@macros.expose_unhygienic  # noqa: F811
def log(x):
    print(x)
