# -*- coding: utf-8 -*-
from macropy.core.test.failure_macro import macros, f, g, h, i


def run1():
    return f[0]


def run2():
    return g[0]


def run3():
    with h:
        pass


def run4():
    @i
    def x():
        pass
