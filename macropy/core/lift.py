from macropy.core.macros import *

macros = True


def u(node):
    "Stub to make the IDE happy"


class Literal(object):
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return self.string
    _fields = []

def unquote_search(node):
    if isinstance(node, BinOp) and type(node.left) is Name and type(node.op) is Mod:
        if 'u' == node.left.id:
            return Literal("ast_repr("+ unparse_ast(node.right) + ")")
        if 'name' == node.left.id:
            return Literal("Name(id = "+unparse_ast(node.right) + ")")
        if 'ast' == node.left.id:
            return Literal(unparse_ast(node.right))

    return node

@expr_macro
def q(node):
    node = Walker(unquote_search).recurse(node)
    out = parse_expr(real_repr(node))
    return out

@block_macro
def q(node):
    body = Walker(unquote_search).recurse(node.body)
    out = parse_stmt(node.optional_vars.id + " = " + "["+",".join(map(real_repr, body))+"]")
    return out
