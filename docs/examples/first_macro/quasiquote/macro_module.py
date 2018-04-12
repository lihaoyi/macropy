# -*- coding: utf-8 -*-
from macropy.core.macros import Macros
from macropy.core.quotes import macros, q, ast_literal, u

macros = Macros()  # noqa: F811


@macros.expr
def expand(tree, **kw):
    addition = 10
    return q[lambda x: x * ast_literal[tree] + u[addition]]
