import macropy.core
import macropy.core.macros

macros = macropy.core.macros.Macros()

@macros.expr
def expr_macro(tree, args, **kw):
    assert list(map(macropy.core.unparse, args)) == ["(1 + math.sqrt(5))"], macropy.core.unparse(args)
    return tree

@macros.block
def block_macro(tree, args, **kw):
    assert list(map(macropy.core.unparse, args)) == ["(1 + math.sqrt(5))"], macropy.core.unparse(args)
    return tree

@macros.decorator
def decorator_macro(tree, args, **kw):
    assert list(map(macropy.core.unparse, args)) == ["(1 + math.sqrt(5))"], macropy.core.unparse(args)
    return tree
