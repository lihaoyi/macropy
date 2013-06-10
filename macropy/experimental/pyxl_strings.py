
from macropy.core.macros import *


import tokenize
from pyxl.codec.tokenizer import pyxl_tokenize



macros = Macros()


@macros.expr
def p(tree, **kw):
    import StringIO
    new_string = tokenize.untokenize(pyxl_tokenize(StringIO.StringIO('(' + tree.s + ')').readline)).rstrip().rstrip("\\")
    total_string = "from __future__ import unicode_literals;" + new_string
    new_tree = ast.parse(total_string)
    return new_tree.body[1].value
