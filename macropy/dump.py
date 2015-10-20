from macropy.core.macros import *
from macropy.core.hquotes import macros, hq, u, ast, ast_list

macros = Macros()

@macros.expr
def dump(tree, **kw):
    """Macro to dump a literal expression and its value so we DRY."""
    return hq[unparse(tree) + ' = ' + str(ast[tree])]
