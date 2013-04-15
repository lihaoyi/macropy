import re

from macroscopy.core.macros import *
from macroscopy.core.lift import *

def wrap(printer, txt, x):

    string = txt + " -> " + repr(x)

    printer(string)

    return x

@expr_macro
def log(node):
    new_node = q%(wrap(lambda x: log(x), u%unparse(node), ast%node))
    return new_node

from ast import *
@expr_macro
def trace(node):

    def func(node):
        print "Tracing", node

        if isinstance(node, AST) and \
                node._fields != () and \
                type(node) is not Num and \
                type(node) is not Str and \
                type(node) is not Name:

            txt = unparse(node)
            for field, old_value in list(iter_fields(node)):
                print field
                print old_value
                old_value = getattr(node, field, None)

                new_value = Macros.recurse(old_value, func, autorecurse=False)

                setattr(node, field, new_value)


            wrapped = q%(wrap(lambda x: log(x), u%txt, ast%node))
            return wrapped
        else:
            return node

    return Macros.recurse(node, func, autorecurse=False)
