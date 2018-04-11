# -*- coding: utf-8 -*-
from macropy.core.macros import Macros

macros = Macros()


@macros.block
def expand(tree, **kw):
    import copy
    return tree * 10
