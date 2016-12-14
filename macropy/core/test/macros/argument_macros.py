from macropy.core.macros import *

macros = Macros()

@macros.expr
def expr_macro(tree, args, **kw):
    assert list(map(unparse, args)) == ["(1 + math.sqrt(5))"], unparse(args)
    return tree

@macros.block
def block_macro(tree, args, **kw):
    assert list(map(unparse, args)) == ["(1 + math.sqrt(5))"], unparse(args)
    return tree

@macros.decorator
def decorator_macro(tree, args, **kw):
    assert list(map(unparse, args)) == ["(1 + math.sqrt(5))"], unparse(args)
    return tree
