# -*- coding: utf-8 -*-
from macropy.core.macros import Macros
from macropy.core.hquotes import macros, hq, u, ast_literal

macros = Macros()  # noqa: F811


@macros.expr
def log(tree, exact_src, **kw):
    new_tree = hq[wrap(u[exact_src(tree)], ast_literal[tree])]
    return new_tree


def wrap(txt, x):
    print(txt + " -> " + repr(x))
    return x
