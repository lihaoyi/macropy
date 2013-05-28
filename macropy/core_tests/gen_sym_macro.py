from macropy.core.macros import *

macros = Macros()

@macros.expr()
def f(tree, gen_sym, **kw):
    symbols = [gen_sym(), gen_sym(), gen_sym(), gen_sym(), gen_sym()]
    assert symbols == ["sym0", "sym2", "sym5", "sym6", "sym7"], symbols
    return Num(n = 10)
