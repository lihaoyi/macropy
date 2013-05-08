
from macropy.core.macros import *
from macropy.core.lift import macros, q, u
import ast


macros = Macros()

def wrap(printer, txt, x):
    string = txt + " -> " + repr(x)
    printer(string)
    return x


@macros.expr
def log(tree):
    new_tree = q%(wrap(log, u%unparse_ast(tree), ast%tree))
    return new_tree



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

        def func(tree):

            if isinstance(tree, expr) and \
                            tree._fields != () and \
                            type(tree) is not Num and \
                            type(tree) is not Str and \
                            type(tree) is not Name:

                try:
                    literal_eval(tree)
                    return tree
                except ValueError:
                    txt = unparse_ast(tree)
                    self.walk_children(tree)
                    if self.registry is not None:
                        self.registry.append([txt, tree])
                        return tree
                    else:
                        wrapped = q%(wrap(log, u%txt, ast%tree))
                        return wrapped
            elif isinstance(tree, stmt):
                txt = unparse_ast(tree).strip()
                self.walk_children(tree)
                with q as code:
                    log(u%txt)

                return [code, tree]
            else:
                return tree
        self.func = func

@macros.expr
def trace(tree):
    ret = _TraceWalker().recurse(tree)
    return ret

@macros.block
def trace(tree):
    ret = _TraceWalker().recurse(tree.body)
    return ret


def require_log(stuff):
    s = "\n".join(txt + " -> " + str(tree) for [txt, tree] in stuff)
    raise AssertionError("Require Failed\n" + s)

def _require_transform(tree):

    walker = _TraceWalker([])
    walker.recurse(tree)

    registry = [List(elts = [ast_repr(s), t]) for s, t in walker.registry]
    new = q%(ast%tree or require_log([ast%registry]))

    return new

@macros.expr
def require(tree):
    return _require_transform(tree)

@macros.block
def require(tree):
    for expr in tree.body:
        expr.value = _require_transform(expr.value)

    return tree.body

def log(x): print x