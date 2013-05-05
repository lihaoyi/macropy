
from macropy.core.macros import *

from pyxl.codec.register import pyxl_transform_string

macros = Macros()

@macros.expr
def p(tree):
    new_string = pyxl_transform_string('(' + tree.s + ')')
    new_tree = ast.parse("from __future__ import unicode_literals;" + new_string)
    return new_tree.body[1].value
