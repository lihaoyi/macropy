from macropy.core.macros import *
from macropy.core import *
macros = Macros()

def u(tree):
    """Stub to make the IDE happy"""

def name(tree):
    """Stub to make the IDE happy"""
def ast(tree):
    """Stub to make the IDE happy"""
def ast_list(tree):
    """Stub to make the IDE happy"""
def extract(tree):
    if isinstance(tree, Subscript) and type(tree.slice) is Index:
        return tree.value.id, tree.slice.value

@Walker
def _unquote_search(tree, **kw):

    e = extract(tree)

    if e:
        func, right = e

        if 'u' == func:
            return Literal(Call(Name(id="ast_repr"), [right], [], None, None))
        elif 'name' == func:
            return Literal(Call(Name(id="Name"), [], [keyword("id", right)], None, None))
        elif 'ast' == func:
            return Literal(right)
        elif 'ast_list' == func:
            return Literal(Call(Name(id="List"), [], [keyword("elts", right)], None, None))


@macros.expr()
def q(tree, **kw):
    tree = _unquote_search.recurse(tree)
    return ast_repr(tree)


@macros.block()
def q(tree, target, **kw):
    body = _unquote_search.recurse(tree)
    return [Assign([Name(id=target.id)], ast_repr(body))]
