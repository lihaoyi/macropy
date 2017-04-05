import ast

import macropy.core.macros

macros = macropy.core.macros.Macros()

@macros.expr
def f(tree, gen_sym, **kw):
    symbols = [gen_sym(), gen_sym(), gen_sym(), gen_sym(), gen_sym()]
    assert symbols == ["sym2", "sym5", "sym6", "sym7", "sym8"], symbols
    renamed = [gen_sym("max"), gen_sym("max"), gen_sym("run"), gen_sym("run")]
    assert renamed == ["max1", "max2", "run1", "run2"], renamed
    unchanged = [gen_sym("grar"), gen_sym("grar"), gen_sym("omg"), gen_sym("omg")]
    assert unchanged == ["grar", "grar1", "omg", "omg1"], unchanged
    return ast.Num(n = 10)
