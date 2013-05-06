from macropy.core.macros import *

macros = Macros()

def u(node):
    """Stub to make the IDE happy"""


class Literal(object):
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return unparse_ast(self.body)

    _fields = []


@Walker
def _unquote_search(node):
    if isinstance(node, BinOp) and type(node.left) is Name and type(node.op) is Mod:
        if 'u' == node.left.id:
            x = parse_expr("ast_repr(x)")
            x.args[0] = node.right
            return Literal(x)
        if 'name' == node.left.id:
            x = parse_expr("Name(id = x)")
            x.keywords[0].value = node.right
            return Literal(x)
        if 'ast' == node.left.id:
            return Literal(node.right)
        if 'ast_list' == node.left.id:
            x = parse_expr("List(elts = x)")
            x.keywords[0].value = node.right
            return Literal(x)
    return node


@macros.expr
def q(node):
    node = _unquote_search.recurse(node)
    return parse_expr(real_repr(node))


@macros.block
def q(node):
    body = _unquote_search.recurse(node.body)
    return parse_stmt(node.optional_vars.id + " = " + real_repr(body))
