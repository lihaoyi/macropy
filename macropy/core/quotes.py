"""Implementation of the Quasiquotes macro.

`u`, `name`, `ast` and `ast_list` are the unquote delimiters, used to
interpolate things into a quoted section.
"""
from macropy.core.macros import *

macros = Macros()


@singleton
class u():
    def wrap(self, tree):
        return Literal(Call(Name(id="ast_repr"), [tree], [], None, None))


@singleton
class name():
    def wrap(self, tree):
        return Literal(Call(Name(id="Name"), [], [keyword("id", tree)], None, None))


@singleton
class ast():
    def wrap(self, tree):
        return Literal(tree)


@singleton
class ast_list():
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
    body = unquote_search.recurse(tree)
    new_body = ast_repr(body)
    return [Assign([target], new_body)]

