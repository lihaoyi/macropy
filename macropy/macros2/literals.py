import re

from macropy.core.macros import *

macros = Macros()

@macros.expr
def bin(node):
    assert type(node) is Num
    return Num(int(str(node.n), 2))

@macros.expr
def oct(node):
    assert type(node) is Num
    return Num(int(str(node.n), 8))

@macros.expr
def hex(node):
    assert type(node) is Name
    return Num(int(node.id, 16))

