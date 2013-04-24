
from macropy.core.macros import *
from macropy.core.lift import *
import ast


def wrap(printer, txt, x):
    string = txt + " -> " + repr(x)
    printer(string)
    return x


@expr_macro
def log(node):
    new_node = q%(wrap(log, u%unparse(node), u%node))
    return new_node



class TraceWalker(Walker):
    def __init__(self, registry=None):
        self.autorecurse = False
        self.registry = registry

        def func(node):

            if isinstance(node, expr) and \
                            node._fields != () and \
                            type(node) is not Num and \
                            type(node) is not Str and \
                            type(node) is not Name:

                txt = unparse(node)
                self.walk_children(node)

                if self.registry is not None:
                    self.registry.append([txt, node])
                    return node
                else:
                    wrapped = q%(wrap(log, u%txt, u%node))
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
    ret = TraceWalker().recurse(node)
    return ret

@block_macro
def trace(node):
    ret = TraceWalker().recurse(node.body)
    return ret



def require_log(stuff):
    s = "\n".join(txt + " -> " + str(tree) for [txt, tree] in stuff)
    raise AssertionError("Require Failed\n" + s)

def require_transform(node):
    walker = TraceWalker([])
    ret = walker.recurse(node)

    registry = List(elts = [List(elts = [ast_repr(s), t]) for s, t in walker.registry])
    new = q%(u%node or require_log(u%registry))

    return new

@expr_macro
def require(node):
    return require_transform(node)

@block_macro
def require(node):
    for expr in node.body:
        expr.value = require_transform(expr.value)

    return node.body