import ast
from ast import *
from macroscopy.unparser import unparse_ast
from macroscopy.macros import *
from macroscopy.lift import *

@macro
def log(node):
    return q%printWrap(
        u%(str(node.lineno) + "\t| " + unparse(node)),
        lambda: u%node
    )
@macro
def tracer(node):
    def trace_stmt(node):
        return ast.parse("print %s" % repr(
            str(node.lineno) + "\t| " + unparse(node)[1:].replace('\n', '\n\t| ')
        )).body[0]

    def trace_expr(node):
        tree = q%printWrap(
            u%(str(node.lineno) + "\t| " + unparse(node)),
            lambda: u%node
        )

        return tree

    def func(node):
        try:
            if isinstance(node, stmt):
                return [trace_stmt(node), node]
            elif hasattr(node, "ctx") and type(node.ctx) == Store:
                return node
            elif type(node) is Name:
                return node
            elif isinstance(node, expr):
                return trace_expr(node)
            else:
                return node
        finally:
            Macros.recurse(node, func)
    return [func(child) for child in node.body]


def printWrap(txt, thunk):
    print txt
    return thunk()