
from macropy.core.macros import *

import sys
import tokenize
from pyxl.codec.tokenizer import pyxl_tokenize
from pyxl.html import *



macros = Macros()

@macros.expr()
def p(tree):
    import StringIO
    new_string = tokenize.untokenize(pyxl_tokenize(StringIO.StringIO('(' + tree.s + ')').readline)).rstrip()
    new_tree = ast.parse("from __future__ import unicode_literals;" + new_string)
    return new_tree.body[1].value
