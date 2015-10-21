from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, u, ast, ast_list

macros = Macros()

@macros.expr
def dump(tree, **kw):
    """Macro to dump a literal expression and its value so we DRY."""
    return hq[unparse(tree) + ' ~~> ' + str(ast[tree])]

def _fuggle_3bf1b522_f487_4386_9466_62308ef1f105(x):
    print x
    return None

@macros.expr
def dumpid(tree, **kw):
    """Macro with the semantics of identity that prints an expression and its value
as a side effect and returns the value"""
    return hq[(_fuggle_3bf1b522_f487_4386_9466_62308ef1f105(unparse(tree) + ' ~~> ' + str(ast[tree])), ast[tree])[1]]
