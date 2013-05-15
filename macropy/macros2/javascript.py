from macropy.core.macros import *
from macropy.core.lift import macros, q, u, ast
import pjs
from pjs.converter import Scope

std_lib = [
    'modules.js',
    'functions.js',
    'classes.js',
    '__builtin__.js',
]

std_lib_script = "\n".join(open("pjs/jslib/" + f).read() for f in std_lib)

macros = Macros()

@macros.expr()
def js(tree):
    javascript = pjs.converter.Converter("").convert_node(tree, Scope())
    return Str(javascript)

@macros.expr()
def pyjs(tree):
    javascript = pjs.converter.Converter("").convert_node(tree, Scope())
    return q%(ast%tree, u%javascript)
