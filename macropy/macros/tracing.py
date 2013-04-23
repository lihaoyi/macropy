
from macropy.core.macros import *
from macropy.core.lift import *

def wrap(printer, txt, x):

    string = txt + " -> " + repr(x)

    printer(string)

    return x

@expr_macro
def log(node):
    new_node = q%(wrap(log, u%unparse(node), ast%node))
    return new_node


@singleton
class TraceWalker(Walker):
    def __init__(self):
        self.autorecurse = False

        def func(node):

            if isinstance(node, expr) and \
                            node._fields != () and \
                            type(node) is not Num and \
                            type(node) is not Str and \
                            type(node) is not Name:

                txt = unparse(node)
                self.walk_children(node)

                wrapped = q%(wrap(log, u%txt, ast%node))
                return wrapped
            elif isinstance(node, stmt):
                txt = unparse(node).strip()
                self.walk_children(node)
                with q as code:
                    log(u%txt)
                return [code, node]
            else:
                return node
        self.func = func

@expr_macro
def trace(node):
    ret = TraceWalker.recurse(node)
    return ret

@block_macro
def trace(node):
    ret = TraceWalker.recurse(node.body)
    return ret
