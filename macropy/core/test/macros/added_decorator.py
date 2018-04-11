# -*- coding: utf-8 -*-
from .added_decorator_macro import macros, my_macro, my_macro2  # noqa: F401


def outer(x):
    def wrapper():
        return x() + 1
    return wrapper


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
