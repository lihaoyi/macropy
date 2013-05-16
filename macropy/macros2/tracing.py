
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
def log(tree):
    new_tree = q%(wrap(log, u%unparse_ast(tree), ast%tree))
    return new_tree

@Walker
def trace_walk(tree, ctx):
    if isinstance(tree, expr) and \
            tree._fields != () and \
            type(tree) is not Num and \
            type(tree) is not Str and \
            type(tree) is not Name:

        try:
            literal_eval(tree)
            return tree, stop
        except ValueError:
            txt = unparse_ast(tree)
            trace_walk.walk_children(tree)

            wrapped = q%(wrap(log, u%txt, ast%tree))
            return wrapped, stop

    elif isinstance(tree, stmt):
        txt = unparse_ast(tree).strip()
        trace_walk.walk_children(tree)
        with q as code:
            log(u%txt)

        return [code, tree], stop

@macros.expr()
def trace(tree):
    ret = trace_walk.recurse(tree, None)
    return ret

@macros.block()
def trace(tree):
    ret = trace_walk.recurse(tree.body, None)
    return ret


def _require_transform(tree):

    ret = trace_walk.recurse(copy.deepcopy(tree), None)
    trace_walk.recurse(copy.deepcopy(tree), None)
    new = q%(ast%tree or handle(lambda log: ast%ret))
    return new

def handle(thunk):
    out = []
    thunk(out.append)
    raise AssertionError("Require Failed\n" + "\n".join(out))

@macros.expr()
def require(tree):
    return _require_transform(tree)

@macros.block()
def require(tree):
    for expr in tree.body:
        expr.value = _require_transform(expr.value)

    return tree.body

def log(x): print x
