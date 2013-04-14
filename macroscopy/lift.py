
from macros import *
from ast import *


def u(node):
    """Stub to make the IDE happy"""
    pass


@macro
def q(node):
    """
    Quotes the target node. This lifts the target AST from compile-time to
    load-time, making it available to the caller. Also provides an unquote
    facility to interpolate run-time values into the compile-time lifted AST.
    """

    unquotes = []
    def unquote_search(node):
        if isinstance(node, BinOp) and type(node.left) is Name and type(node.op) is Mod:
            if 'u' == node.left.id:
                unquotes.append(node.right)
                return placeholder
            if 'ast' == node.left.id:
                unquotes.append(node.right)
                tree = parse_expr("eval(unparse(1))")
                tree.args[0].args[0] = placeholder
                return tree
        return Macros.recurse(node, unquote_search)

    node = unquote_search(node)
    unquote_calcs = [unparse(u) for u in unquotes]
    out = parse_expr("interpolate_ast("+repr(node)+",["+",".join(unquote_calcs)+"])")
    return out


