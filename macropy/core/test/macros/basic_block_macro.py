import macropy.core
import macropy.core.macros

macros = macropy.core.macros.Macros()

@macros.block
def my_macro(tree, target, **kw):
    assert macropy.core.unparse(target) == "y"
    assert macropy.core.unparse(tree).strip() == "x = (x + 1)", macropy.core.unparse(tree)
    return tree * 3
