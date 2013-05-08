import re

from macropy.core.macros import *

macros = Macros()

@macros.expr
def bin(tree):
    assert type(tree) is Num
    return Num(int(str(tree.n), 2))

@macros.expr
def oct(tree):
    assert type(tree) is Num
    return Num(int(str(tree.n), 8))

@macros.expr
def hex(tree):
    assert type(tree) is Name
    return Num(int(tree.id, 16))

