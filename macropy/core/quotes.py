"""Implementation of the Quasiquotes macro.

`u`, `name`, `ast_literal` and `ast_list` are the unquote delimiters, used to
interpolate things into a quoted section.
"""

import ast
import sys

from macropy.core import ast_repr, Literal
import macropy.core.macros
import macropy.core.walkers

macros = macropy.core.macros.Macros()

@macropy.core.walkers.Walker
def unquote_search(tree, **kw):

    res = macropy.core.macros.check_annotated(tree)
    if res:
        func, right = res
        for f in [u, name, ast_literal, ast_list]:
            # print('Unquote search %s' % f, file=sys.stderr)
            if f.__name__ == func:
                return f(right)



@macros.expr
def q(tree, **kw):
    tree = unquote_search.recurse(tree)
    tree = ast_repr(tree)
    print('Quote expr %s' % ast.dump(tree) if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    return tree


@macros.block
def q(tree, target, **kw):
    """Quasiquote macro, used to lift sections of code into their AST
    representation which can be manipulated at runtime. Used together with
    the `u`, `name`, `ast_literal`, `ast_list` unquotes."""
    body = unquote_search.recurse(tree)
    new_body = ast_repr(body)
    return [ast.Assign([target], new_body)]


@macropy.core.macros.macro_stub
def u(tree):
    """Splices a value into the quoted code snippet, converting it into an AST
    via ast_repr"""
    return Literal(ast.Call(ast.Name(id="ast_repr"), [tree], [], None, None))


@macropy.core.macros.macro_stub
def name(tree):
    "Splices a string value into the quoted code snippet as a Name"
    return Literal(ast.Call(ast.Name(id="Name"), [], [ast.keyword("id", tree)], None, None))


@macropy.core.macros.macro_stub
def ast_literal(tree):
    "Splices an AST into the quoted code snippet"
    return Literal(tree)


@macropy.core.macros.macro_stub
def ast_list(tree):
    """Splices a list of ASTs into the quoted code snippet as a List node"""
    return Literal(ast.Call(ast.Name(id="List"), [], [ast.keyword("elts", tree)], None, None))

