# -*- coding: utf-8 -*-
from macropy.core.macros import Macros
from macropy.core.hquotes import macros, hq, u, unhygienic, ast_literal

macros = Macros()  # noqa: F811


@macros.expr
def log(tree, exact_src, **kw):
    new_tree = hq[wrap(unhygienic[log_func], u[exact_src(tree)],
                       ast_literal[tree])]
    return new_tree


def wrap(printer, txt, x):
    printer(txt + " -> " + repr(x))
    return x


@macros.expose_unhygienic
def log_func(txt):
    print(txt)
