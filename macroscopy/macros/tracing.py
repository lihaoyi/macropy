import re

from macroscopy.core.macros import *
from macroscopy.core.lift import *

def wrap(printer, txt, x):
    print "omg", x
    string = txt + " -> " + repr(x)

    printer(string)

    return x

@expr_macro
def log(node):
    new_node = q%(wrap(lambda x: log(x), u%unparse(node), ast%node))
    return new_node

@expr_macro
def trace(node):
    print "Tracing", node

    def func(node):
        if isinstance(node, expr) and \
                type(node) is not Num and \
                type(node) is not Str and \
                type(node) is not Name:
            txt = unparse(node)
            new_node = Macros.recurse(node, func)
            wrapped = q%(wrap(lambda x: log(x), u%txt, ast%new_node))
            return wrapped
        else:
            return node


    return func(node)


