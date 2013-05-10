"""
This file contains the basic operations necessary to transform between
code in various forms: Source, ASTs, and Values. These operations wrap
more primitive forms (e.g. in the ast module) which should not be used
directly.

This map maps out how to convert from form to form:

                     parse_stmt
       ____________  parse_expr  ____________
      |            |----------->|            |
      |   Source   |            |    AST     |
      |____________|<-----------|____________|
          ^     |   unparse_ast   |        ^
          |     |                 | eval   | ast_repr
          |     |                 |        |
real_repr |     |    eval        _v________|_
          |     --------------->|            |
          |                     |   Value    |
          ----------------------|____________|
"""
import ast
from unparser import Unparser

import StringIO

def ast_repr(x):
    """Similar to repr(), but returns an AST instead of a String, which when
    evaluated will return the given value."""
    return parse_expr(repr(x))


def parse_expr(x):
    """Parses a string into an `expr` AST"""
    return ast.parse(x).body[0].value


def parse_stmt(x):
    """Parses a string into an `stmt` AST"""
    return ast.parse(x).body


def real_repr(thing):
    """Converts the given value into a string which when evaluated will
    return the value. This one is smart enough to take care of ASTs"""
    if isinstance(thing, ast.AST):
        fields = [(a, real_repr(b)) for a, b in ast.iter_fields(thing)]
        rv = '%s(%s' % (thing.__class__.__name__, ', '.join(
            (b for a, b in fields)
        ))

        return rv + ')'
    elif isinstance(thing, list):
        return '[%s]' % ', '.join(real_repr(x) for x in thing)
    return repr(thing)


def unparse_ast(ast):
    """Converts an AST back into the source code from whence it came!"""
    buffer = StringIO.StringIO()
    Unparser(ast, buffer)
    return buffer.getvalue()
