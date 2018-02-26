# -*- coding: utf-8 -*-
import macropy.core
import macropy.core.macros

macros = macropy.core.macros.Macros()


@macros.decorator
def my_macro(tree, **kw):
    assert macropy.core.unparse(tree).strip() == "\n".join([
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    return x"]), macropy.core.unparse(tree)

    b = tree.body
    tree.body = [b[0], b[1], b[1], b[1], b[1], b[2]]
    return tree


@macros.decorator
def my_macro2(tree, **kw):
    assert macropy.core.unparse(tree).strip() == "\n".join([
    "@middle",
    "@my_macro",
    "@inner",
    "def run():",
    "    x = 10",
    "    x = (x + 1)",
    "    return x"]), macropy.core.unparse(tree)

    return tree
