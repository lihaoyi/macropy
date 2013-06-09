from macropy.core.macros import *
from macropy.core.quotes import macros, q, u, ast
import pjs
from pjs.converter import Scope

std_lib = [
    'modules.js',
    'functions.js',
    'classes.js',
    '__builtin__.js',
]

import os
path = os.path.dirname(pjs.__file__) + "/data/pjslib.js"
std_lib_script = open(path).read()

macros = Macros()


@macros.expr
def js(tree, **kw):
    javascript = pjs.converter.Converter("").convert_node(tree, Scope())
    return Str(javascript)


@macros.expr
def pyjs(tree, **kw):
    javascript = pjs.converter.Converter("").convert_node(tree, Scope())
    return q[(ast[tree], u[javascript])]
