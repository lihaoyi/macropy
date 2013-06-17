"""Implementation of the Quasiquotes macro.

`u`, `name`, `ast` and `ast_list` are the unquote delimiters, used to
interpolate things into a quoted section.
"""
from macropy.core.macros import *


macros = Macros()


@singleton
class u():
    """Splices a value into the quoted code snippet, converting it into an AST
    via ast_repr"""
    def wrap(self, tree):
        return Literal(Call(Name(id="ast_repr"), [tree], [], None, None))


@singleton
class name():
    "Splices a string value into the quoted code snippet as a Name"
    def wrap(self, tree):
        return Literal(Call(Name(id="Name"), [], [keyword("id", tree)], None, None))


@singleton
class ast():
    "Splices an AST into the quoted code snippet"
    def wrap(self, tree):
        return Literal(tree)


@singleton
class ast_list():
    """Splices a list of ASTs into the quoted code snippet as a List node"""
    def wrap(self, tree):
        return Literal(Call(Name(id="List"), [], [keyword("elts", tree)], None, None))


@Walker
def unquote_search(tree, **kw):

    res = check_annotated(tree)
    if res:
        func, right = res

        if 'u' == func:
            return u.wrap(right)
        elif 'name' == func:
            return name.wrap(right)
        elif 'ast' == func:
            return ast.wrap(right)
        elif 'ast_list' == func:
            return ast_list.wrap(right)


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

