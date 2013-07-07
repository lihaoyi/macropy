from macropy.core.failure import MacroExpansionError
from macropy.core.macros import *

macros = Macros()

@macros.expr
def f(tree, gen_sym, **kw):
    raise Exception("i am a cow")

@macros.expr
def g(tree, gen_sym, **kw):
    raise MacroExpansionError("i am a cow")
