import re

from macropy.core.macros import *

macros = True

@expr_macro
def bin(node):
    assert type(node) is Num
    return Num(int(str(node.n), 2))

@expr_macro
def oct(node):
    assert type(node) is Num
    return Num(int(str(node.n), 8))

@expr_macro
def hex(node):
    assert type(node) is Name
    return Num(int(node.id, 16))

