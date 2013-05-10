from macropy.core.macros import *
from macropy.core import *
macros = Macros()

def u(tree):
    """Stub to make the IDE happy"""
def name(tree):
    """Stub to make the IDE happy"""


class Literal(object):
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return unparse_ast(self.body)

    _fields = []


@Walker
def _unquote_search(tree):
    if isinstance(tree, BinOp) and type(tree.left) is Name and type(tree.op) is Mod:
        if 'u' == tree.left.id:
            x = parse_expr("ast_repr(x)")
            x.args[0] = tree.right
            return Literal(x)
        if 'name' == tree.left.id:
            x = parse_expr("Name(id = x)")
            x.keywords[0].value = tree.right
            return Literal(x)
        if 'ast' == tree.left.id:
            return Literal(tree.right)
        if 'ast_list' == tree.left.id:
            x = parse_expr("List(elts = x)")
            x.keywords[0].value = tree.right
            return Literal(x)
    return tree


@macros.expr
def q(tree):
    tree = _unquote_search.recurse(tree)

    return parse_expr(real_repr(tree))


@macros.block
def q(tree):
    body = _unquote_search.recurse(tree.body)
    return parse_stmt(tree.optional_vars.id + " = " + real_repr(body))
