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


def ast_repr(x):
    return ast.parse(repr(x))


def parse_expr(x):
    return ast.parse(x).body[0].value


def parse_stmt(x):
    return ast.parse(x).body

def unparse(ast):
    import StringIO
    buffer = StringIO.StringIO()
    Unparser(ast, buffer)
    return buffer.getvalue()