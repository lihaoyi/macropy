from macropy.core.macros import *

macros = Macros()

@macros.decorator
def my_macro(tree, **kw):
    assert unparse(tree).strip() == "\n".join([
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    return x"]), unparse(tree)

    b = tree.body
    tree.body = [b[0], b[1], b[1], b[1], b[1], b[2]]
    return tree

@macros.decorator
def my_macro2(tree, **kw):
    assert unparse(tree).strip() == "\n".join([
    "@middle",
    "@my_macro",
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    return x"]), unparse(tree)

    return tree
