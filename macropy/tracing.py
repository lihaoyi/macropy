
from macropy.core.macros import *
from macropy.core.hquotes import macros, u, hq, unhygienic

import copy

macros = Macros()


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
    new_tree = hq[wrap(unhygienic[log], u[exact_src(tree)], ast[tree])]
    return new_tree


@macros.expr
def show_expanded(tree, expand_macros,  **kw):
    expanded_tree = expand_macros(tree)
    new_tree = hq[wrap_simple(unhygienic[log], u[unparse(expanded_tree)], ast[expanded_tree])]
    return new_tree


@macros.block
def show_expanded(tree, expand_macros, **kw):
    new_tree = []
    for stmt in tree:
        new_stmt = expand_macros(stmt)

        with hq as code:
            unhygienic[log](u[unparse(new_stmt)])
        new_tree.append(code)
        new_tree.append(new_stmt)

    return new_tree


def trace_walk_func(tree, exact_src):
    @Walker
    def trace_walk(tree, stop, **kw):

        if isinstance(tree, expr) and \
                tree._fields != () and \
                type(tree) is not Name:

            try:
                literal_eval(tree)
                stop()
                return tree
            except ValueError:
                txt = exact_src(tree)
                trace_walk.walk_children(tree)

                wrapped = hq[wrap(unhygienic[log], u[txt], ast[tree])]
                stop()
                return wrapped

        elif isinstance(tree, stmt):
            txt = exact_src(tree)
            trace_walk.walk_children(tree)
            with hq as code:
                unhygienic[log](u[txt])
            stop()
            return [code, tree]

    return trace_walk.recurse(tree)


@macros.expr
def trace(tree, exact_src, **kw):
    ret = trace_walk_func(tree, exact_src)
    return ret


@macros.block
def trace(tree, exact_src, **kw):
    ret = trace_walk_func(tree, exact_src)

    return ret


def require_transform(tree, exact_src):
    ret = trace_walk_func(copy.deepcopy(tree), exact_src)
    trace_walk_func(copy.deepcopy(tree), exact_src)
    new = hq[ast[tree] or wrap_require(lambda log: ast[ret])]
    return new


def wrap_require(thunk):
    out = []
    thunk(out.append)
    raise AssertionError("Require Failed\n" + "\n".join(out))


@macros.expr
def require(tree, exact_src, **kw):
    return require_transform(tree, exact_src)


@macros.block
def require(tree, exact_src, **kw):
    for expr in tree:
        expr.value = require_transform(expr.value, exact_src)

    return tree


@macros.expose_unhygienic
def log(x):
    print(x)
