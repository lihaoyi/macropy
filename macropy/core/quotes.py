# -*- coding: utf-8 -*-
"""Implementation of the Quasiquotes macro.

`u`, `name`, `ast_literal` and `ast_list` are the unquote delimiters, used to
interpolate things into a quoted section.
"""

import ast

from . import ast_repr, compat, Literal, walkers
from .macros import Macros, check_annotated, macro_stub


macros = Macros()


@walkers.Walker
def unquote_search(tree, **kw):
    "Get the values from the helper stubs."
    res = check_annotated(tree)  # returns something if tree == 'foo[...]'
    if res:
        func, right = res
        for f in [u, name, ast_literal, ast_list]:
            # print('Unquote search %s' % f, file=sys.stderr)
            if f.__name__ == func:
                return f(right)


@macros.expr
def q(tree, **kw):
    tree = unquote_search.recurse(tree)
    # print('Quote expr after search %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    tree = ast_repr(tree)
    # print('Quote expr after repr %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    return tree


@macros.block  # noqa: F811
def q(tree, target, **kw):
    """Quasiquote macro, used to lift sections of code into their AST
    representation which can be manipulated at runtime. Used together with
    the `u`, `name`, `ast_literal`, `ast_list` unquotes."""
    body = unquote_search.recurse(tree)
    # print('Quote block after search %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    new_body = ast_repr(body)
    # print('Quote block after repr %s' % ast.dump(tree)
    #       if isinstance(tree, ast.AST) else tree, file=sys.stderr)
    return [ast.Assign([target], new_body)]


@macro_stub
def u(tree):
    """Splices a value into the quoted code snippet, converting it into an AST
    via ast_repr."""
    return Literal(compat.Call(ast.Name(id="ast_repr"), [tree], []))


@macro_stub
def name(tree):
    "Splices a string value into the quoted code snippet as a Name."
    # TODO: another hard-coded call now assuming `ast.Name`
    return Literal(compat.Call(ast.Attribute(
        value=ast.Name(id='ast', ctx=ast.Load()),
        attr='Name', ctx=ast.Load()), [], [ast.keyword("id", tree)]))


@macro_stub
def ast_literal(tree):
    "Splices an AST into the quoted code snippet."
    return Literal(tree)


@macro_stub
def ast_list(tree):
    """Splices a list of ASTs into the quoted code snippet as a List node."""
    return Literal(compat.Call(ast.Attribute(
        value=ast.Name(id='ast', ctx=ast.Load()),
        attr='List', ctx=ast.Load()), [], [ast.keyword("elts", tree)]))


macros.expose_unhygienic(ast)
macros.expose_unhygienic(ast_repr)
macros.expose_unhygienic(Literal)
