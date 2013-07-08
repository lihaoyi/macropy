"""Implementation of the Quasiquotes macro.

`u`, `name`, `ast` and `ast_list` are the unquote delimiters, used to
interpolate things into a quoted section.
"""
from macropy.core.macros import *


macros = Macros()




@Walker
def unquote_search(tree, **kw):

    res = check_annotated(tree)
    if res:
        func, right = res
        for f in [u, name, ast, ast_list]:
            if f.__name__ == func:
                return f(right)



@macros.expr
def q(tree, **kw):
    tree = unquote_search.recurse(tree)
    tree = ast_repr(tree)
    return tree


@macros.block
def q(tree, target, **kw):
    """Quasiquote macro, used to lift sections of code into their AST
    representation which can be manipulated at runtime. Used together with
    the `u`, `name`, `ast`, `ast_list` unquotes."""
    body = unquote_search.recurse(tree)
    new_body = ast_repr(body)
    return [Assign([target], new_body)]


@macro_stub
def u(tree):
    """Splices a value into the quoted code snippet, converting it into an AST
    via ast_repr"""
    return Literal(Call(Name(id="ast_repr"), [tree], [], None, None))


@macro_stub
def name(tree):
    "Splices a string value into the quoted code snippet as a Name"
    return Literal(Call(Name(id="Name"), [], [keyword("id", tree)], None, None))


@macro_stub
def ast(tree):
    "Splices an AST into the quoted code snippet"
    return Literal(tree)


@macro_stub
def ast_list(tree):
    """Splices a list of ASTs into the quoted code snippet as a List node"""
    return Literal(Call(Name(id="List"), [], [keyword("elts", tree)], None, None))

