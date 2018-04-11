# -*- coding: utf-8 -*-
from macropy.core import unparse
from macropy.core.macros import Macros
from macropy.core.hquotes import macros, hq

macros = Macros()  # noqa: F811


def added_decorator(func):
    def wrapper():
        return func() / 2
    return wrapper

@macros.decorator
def my_macro(tree, **kw):
    assert unparse(tree).strip() == "\n".join([
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    return x"]), unparse(tree)

    b = tree.body
    tree.body = [b[0], b[1], b[1], b[1], b[1], b[2]]
    tree.decorator_list = [hq[added_decorator]] + tree.decorator_list
    return tree


@macros.decorator
def my_macro2(tree, **kw):
    assert unparse(tree).strip() == "\n".join([
    "@middle",
    "@added_decorator",
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    x = (x + 1)",
    "    x = (x + 1)",
    "    x = (x + 1)",
    "    return x"]), unparse(tree)

    return tree
