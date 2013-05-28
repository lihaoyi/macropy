from macropy.core.macros import *

macros = Macros()

@macros.decorator()
def my_macro(tree, **kw):
    assert unparse_ast(tree).strip() == "\n".join([
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    return x"]), unparse_ast(tree)

    b = tree.body
    tree.body = [b[0], b[1], b[1], b[1], b[1], b[2]]
    return tree
