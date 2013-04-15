
from macroscopy.core.macros import *


def u(node):
    """Stub to make the IDE happy"""
    pass

def unquote_search(node, unquotes):
    if isinstance(node, BinOp) and type(node.left) is Name and type(node.op) is Mod:
        if 'u' == node.left.id:
            unquotes.append(node.right)
            return Placeholder()
        if 'ast' == node.left.id:
            unquotes.append(node.right)
            tree = parse_expr("eval(unparse(1))")
            tree.args[0].args[0] = Placeholder()

            return tree
    return node

@expr_macro
def q(node):
    print "EXPR"
    """
    Quotes the target expression. This lifts the target AST from compile-time to
    load-time, making it available to the caller. Also provides an unquote
    facility to interpolate run-time values into the compile-time lifted AST.
    """
    unquotes = []

    node = Macros.recurse(node, lambda x: unquote_search(x, unquotes))
    print node
    unquote_calcs = [unparse(u) for u in unquotes]
    string = "interp_ast("+repr(node)+",["+",".join(unquote_calcs)+"])"

    out = parse_expr(string)

    return out

@block_macro
def q(node):
    print "BLOCK"
    """
    Quotes the target block, which must ba a With block. This lifts the
    AST from compile-time to load-time, making it available to the caller.
    Also provides an unquote facility to interpolate run-time values into
    the compile-time lifted AST.
    """
    unquotes = []
    body = Macros.recurse(node.body, lambda x: unquote_search(x, unquotes))
    unquote_calcs = [unparse(u) for u in unquotes]
    body_txt = "interp_ast("+repr(body)+",["+",".join(unquote_calcs)+"])"
    out = parse_stmt(node.optional_vars.id + " = " + body_txt)
    return out




