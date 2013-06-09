from macropy.core.macros import *

macros = Macros()

@macros.expr
def expr_macro(tree, args, **kw):

    assert map(unparse_ast, args) == ["(1 + math.sqrt(5))"], unparse_ast(args)
    return tree

@macros.block
def block_macro(tree, args, **kw):
    assert map(unparse_ast, args) == ["(1 + math.sqrt(5))"], unparse_ast(args)
    return tree

@macros.decorator
def decorator_macro(tree, args, **kw):
    assert map(unparse_ast, args) == ["(1 + math.sqrt(5))"], unparse_ast(args)
    return tree
