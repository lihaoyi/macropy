from macropy.core.macros import *

macros = Macros()

@macros.block
def my_macro(tree, target, **kw):
    assert unparse_ast(target) == "y"
    assert unparse_ast(tree).strip() == "x = (x + 1)", unparse_ast(tree)
    return tree * 3
