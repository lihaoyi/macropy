
from macropy.core.macros import *
from macropy.core.lift import macros, q, u
import ast
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

@macros.expr()
def log(tree, exact_src, **kw):
    new_tree = q%(wrap(log, u%exact_src(tree), ast%tree))
    return new_tree

@macros.expr()
def show_expanded(tree, expand_macros, **kw):
    import copy
    expanded_tree = unparse_ast(expand_macros(copy.deepcopy(tree)))
    new_tree = q%(wrap_simple(log, u%expanded_tree, ast%tree))
    return new_tree

@macros.block()
def show_expanded(tree, expand_macros, **kw):
    import copy
    new_tree = []
    for stmt in tree:
        txt = unparse_ast(expand_macros(copy.deepcopy(stmt)))
        with q as code:
            log(u%txt)
        new_tree.append(code)
        new_tree.append(stmt)

    return new_tree

@Walker
def trace_walk(tree, ctx, stop, **kw):
    if isinstance(tree, expr) and \
            tree._fields != () and \
            type(tree) is not Num and \
            type(tree) is not Str and \
            type(tree) is not Name:

        try:
            literal_eval(tree)
            stop()
            return tree
        except ValueError:
            txt = ctx(tree)
            trace_walk.walk_children(tree, ctx)

            wrapped = q%(wrap(log, u%txt, ast%tree))
            stop()
            return wrapped

    elif isinstance(tree, stmt):
        txt = ctx(tree)
        trace_walk.walk_children(tree , ctx)
        with q as code:
            log(u%txt)
        stop()
        return [code, tree]

@macros.expr()
def trace(tree, exact_src, **kw):
    ret = trace_walk.recurse(tree, exact_src)
    return ret

@macros.block()
def trace(tree, exact_src, **kw):
    ret = trace_walk.recurse(tree, exact_src)
    return ret


def _require_transform(tree, exact_src):
    ret = trace_walk.recurse(copy.deepcopy(tree), exact_src)
    trace_walk.recurse(copy.deepcopy(tree), exact_src)
    new = q%(ast%tree or handle(lambda log: ast%ret))
    return new

def handle(thunk):
    out = []
    thunk(out.append)
    raise AssertionError("Require Failed\n" + "\n".join(out))

@macros.expr()
def require(tree, exact_src, **kw):
    return _require_transform(tree, exact_src)

@macros.block()
def require(tree, exact_src, **kw):
    for expr in tree:
        expr.value = _require_transform(expr.value, exact_src)

    return tree

def log(x):
    print(x)
