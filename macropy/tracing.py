

# Imports added by remove_from_imports.

import macropy.core
import macropy.core.macros
import ast
import _ast
import macropy.core.walkers


from macropy.core.hquotes import macros, u, hq, unhygienic

import copy

macros = macropy.core.macros.Macros()


def literal_eval(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, numbers, tuples, lists, dicts, booleans,
    and None.
    """
    _safe_names = {'None': None, 'True': True, 'False': False}
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode='eval')
    if isinstance(node_or_string, _ast.Expression):
        node_or_string = node_or_string.body
    def _convert(node):
        if isinstance(node, _ast.Str):
            return node.s
        elif isinstance(node, _ast.Num):
            return node.n
        elif isinstance(node, _ast.Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, _ast.List):
            return list(map(_convert, node.elts))
        elif isinstance(node, _ast.Dict):
            return dict((_convert(k), _convert(v)) for k, v
                        in zip(node.keys, node.values))
        elif isinstance(node, _ast.Name):
            if node.id in _safe_names:
                return _safe_names[node.id]
        elif isinstance(node, _ast.BinOp) and \
             isinstance(node.op, (_ast.Add, _ast.Sub)) and \
             isinstance(node.right, _ast.Num) and \
             isinstance(node.right.n, complex) and \
             isinstance(node.left, _ast.Num) and \
             isinstance(node.left.n, (int, long, float)):
            left = node.left.n
            right = node.right.n
            if isinstance(node.op, _ast.Add):
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
    new_tree = hq[wrap(unhygienic[log], u[exact_src(tree)], ast.ast[tree])]
    return new_tree


@macros.expr
def show_expanded(tree, expand_macros,  **kw):
    """Prints out the expanded version of the wrapped source code, after all
    macros inside it have been expanded"""
    expanded_tree = expand_macros(tree)
    new_tree = hq[wrap_simple(unhygienic[log], u[macropy.core.unparse(expanded_tree)], ast.ast[expanded_tree])]
    return new_tree


@macros.block
def show_expanded(tree, expand_macros, **kw):
    """Prints out the expanded version of the wrapped source code, after all
    macros inside it have been expanded"""
    new_tree = []
    for stmt in tree:
        new_stmt = expand_macros(stmt)

        with hq as code:
            unhygienic[log](u[macropy.core.unparse(new_stmt)])
        new_tree.append(code)
        new_tree.append(new_stmt)

    return new_tree


def trace_walk_func(tree, exact_src):
    @macropy.core.walkers.Walker
    def trace_walk(tree, stop, **kw):

        if isinstance(tree, _ast.expr) and \
                tree._fields != () and \
                type(tree) is not _ast.Name:

            try:
                literal_eval(tree)
                stop()
                return tree
            except ValueError as e:
                txt = exact_src(tree)
                trace_walk.walk_children(tree)
                wrapped = hq[wrap(unhygienic[log], u[txt], ast.ast[tree])]
                stop()
                return wrapped

        elif isinstance(tree, _ast.stmt):
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
    return ret


@macros.block
def trace(tree, exact_src, **kw):
    """Traces the wrapped code, printing out the source code and evaluated
    result of every statement and expression contained within it"""
    ret = trace_walk_func(tree, exact_src)

    return ret


def require_transform(tree, exact_src):
    ret = trace_walk_func(copy.deepcopy(tree), exact_src)
    trace_walk_func(copy.deepcopy(tree), exact_src)
    new = hq[ast.ast[tree] or wrap_require(lambda log: ast.ast[ret])]
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
    return require_transform(tree, exact_src)


@macros.block
def require(tree, exact_src, **kw):
    """A version of assert that traces the expression's evaluation in the
    case of failure. If used as a block, performs this on every expression
    within the block"""
    for expr in tree:
        expr.value = require_transform(expr.value, exact_src)

    return tree


@macros.expose_unhygienic
def log(x):
    print(x)
