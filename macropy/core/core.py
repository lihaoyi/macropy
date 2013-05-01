import ast
from unparser import Unparser
"""
     ____________  parse_expr  ____________
    |            |----------->|            |
    |   Source   |            |    AST     |
    |____________|<-----------|____________|
        ^     |      unparse    |        ^
        |     |                 | eval   | ast_repr
        |     |                 |        |
   repr |     |    eval        _v________|_
        |     --------------->|            |
        |                     |   Value    |
        ----------------------|____________|
"""

from ast import *
old_repr = repr
def my_repr(x):
    if isinstance(x, (expr, stmt, comprehension)):
        return dump(x)
    else:
        return old_repr(x)

# dirty hack to monkeypatch `repr`, since the ast module's AST trees
# don't have proper __repr__s and PyPy doesn't let me monkey patch them
try:
    # this works in CPython
    __builtins__['repr'] = my_repr
except TypeError, e:
    # this works in PyPy
    __builtins__.repr = my_repr

def ast_repr(x):
    return parse_expr(repr(x))


def parse_expr(x):
    return ast.parse(x).body[0].value


def parse_stmt(x):
    return ast.parse(x).body

def unparse(ast):
    import StringIO
    buffer = StringIO.StringIO()
    Unparser(ast, buffer)
    return buffer.getvalue()
