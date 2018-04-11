# -*- coding: utf-8 -*-
import ast
from io import StringIO
import tokenize

try:
    from pyxl.codec.tokenizer import pyxl_tokenize
    from pyxl import html
except ImportError as e:
    raise RuntimeError("External library missing, please install the 'pyxl3'"
                       " package.") from e

from macropy.core.macros import Macros

macros = Macros()


@macros.expr
def p(tree, **kw):
    new_string = tokenize.untokenize(pyxl_tokenize(StringIO('(' + tree.s + ')')
                                                   .readline)).rstrip().rstrip("\\")
    new_tree = ast.parse(new_string)
    return new_tree.body[0].value


# expose to the calling module some symbols
macros.expose_unhygienic(html, 'html')
# these are needed due to bugs in the port to py3, I suppose
rawhtml = html.rawhtml
macros.expose_unhygienic(rawhtml)
unicode = str
macros.expose_unhygienic(unicode, 'unicode')
