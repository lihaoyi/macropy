
from macropy.core.macros import *
from macropy.core.lift import macros, q, u
import ast
import copy

macros = Macros()

def wrap(printer, txt, x):
    string = txt + " -> " + repr(x)
    printer(string)
    return x


@macros.expr()
def log(tree, src_for, **kw):

    new_tree = q%(wrap(log, u%src_for(tree), ast%tree))
    return new_tree

@Walker
def trace_walk(tree, ctx, **kw):
    if isinstance(tree, expr) and \
            tree._fields != () and \
            type(tree) is not Num and \
            type(tree) is not Str and \
            type(tree) is not Name:

        try:
            literal_eval(tree)
            return tree, stop
        except ValueError:
            txt = ctx(tree)
            trace_walk.walk_children(tree, ctx)

            wrapped = q%(wrap(log, u%txt, ast%tree))
            return wrapped, stop

    elif isinstance(tree, stmt):
        txt = unparse_ast(tree).strip()
        trace_walk.walk_children(tree , ctx)
        with q as code:
            log(u%txt)

        return [code, tree], stop

@macros.expr()
def trace(tree, src_for, **kw):
    ret = trace_walk.recurse(tree, src_for)
    return ret

@macros.block()
def trace(tree, src_for, **kw):
    ret = trace_walk.recurse(tree, src_for)
    return ret


def _require_transform(tree, src_for):
    ret = trace_walk.recurse(copy.deepcopy(tree), src_for)
    trace_walk.recurse(copy.deepcopy(tree), src_for)
    new = q%(ast%tree or handle(lambda log: ast%ret))
    return new

def handle(thunk):
    out = []
    thunk(out.append)
    raise AssertionError("Require Failed\n" + "\n".join(out))

@macros.expr()
def require(tree, src_for, **kw):
    return _require_transform(tree, src_for)

@macros.block()
def require(tree, src_for, **kw):
    for expr in tree:
        expr.value = _require_transform(expr.value, src_for)

    return tree

def log(x):
    print(x)
