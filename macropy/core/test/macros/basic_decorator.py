# -*- coding: utf-8 -*-
from macropy.core.test.macros.basic_decorator_macro import (macros, my_macro,
                                                            my_macro2)


def outer(x):
    return x


def middle(x):
    return x


def inner(x):
    return x


@outer
@my_macro2
@middle
@my_macro
@inner
def run():
    x = 10
    x = x + 1
    return x
