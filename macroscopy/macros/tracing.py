import re

from macroscopy.core.macros import *
from macroscopy.core.lift import *

def wrap(printer, txt, x):
    string = txt + " -> " + str(x)
    try:
        printer(string)
    except Exception, e:
        print string
    return x

@expr_macro
def trace(node):
    new_node = q%(wrap((lambda log: lambda x: log(x))(log), u%unparse(node), ast%node))
    return new_node


