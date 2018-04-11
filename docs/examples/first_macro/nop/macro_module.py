# -*- coding: utf-8 -*-
from macropy.core.macros import Macros

macros = Macros()


@macros.expr
def expand(tree, **kw):
    return tree
