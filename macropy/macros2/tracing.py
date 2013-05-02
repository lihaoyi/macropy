
from macropy.core.macros import *
from macropy.core.lift import macros, q, u
import ast


macros = Macros()

def wrap(printer, txt, x):
    string = txt + " -> " + repr(x)
    printer(string)
    return x


@macros.expr
def log(node):
    new_node = q%(wrap(log, u%unparse_ast(node), ast%node))
    return new_node



class _TraceWalker(Walker):
    """
    If registry=None, this transforms the expression tree such that each
    individual subtree is traced as it is evaluated

    If registry=[], the tree is unchanged, and instead a list of individual
    subtrees together with their string representation is placed into the
    registry. This can be retrieved after the recursion is complete.
    """
    def __init__(self, registry=None):
        self.autorecurse = False
        self.registry = registry

        def func(node):

            if isinstance(node, expr) and \
                            node._fields != () and \
                            type(node) is not Num and \
                            type(node) is not Str and \
                            type(node) is not Name:

                try:
                    literal_eval(node)
                    return node
                except ValueError:
                    txt = unparse_ast(node)
                    self.walk_children(node)
                    if self.registry is not None:
                        self.registry.append([txt, node])
                        return node
                    else:
                        wrapped = q%(wrap(log, u%txt, ast%node))
                        return wrapped
            elif isinstance(node, stmt):
                txt = unparse_ast(node).strip()
                self.walk_children(node)
                with q as code:
                    log(u%txt)

                return [code, node]
            else:
                return node
        self.func = func

@macros.expr
def trace(node):
    ret = _TraceWalker().recurse(node)
    return ret

@macros.block
def trace(node):
    ret = _TraceWalker().recurse(node.body)
    return ret


def require_log(stuff):
    s = "\n".join(txt + " -> " + str(tree) for [txt, tree] in stuff)
    raise AssertionError("Require Failed\n" + s)

def _require_transform(node):

    walker = _TraceWalker([])
    walker.recurse(node)

    registry = [List(elts = [ast_repr(s), t]) for s, t in walker.registry]
    new = q%(ast%node or require_log([ast%registry]))

    return new

@macros.expr
def require(node):
    return _require_transform(node)

@macros.block
def require(node):
    for expr in node.body:
        expr.value = _require_transform(expr.value)

    return node.body

def log(x): print x