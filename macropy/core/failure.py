from macropy.core.macros import *

from macropy.core.hquotes import macros, hq
import traceback


class MacroExpansionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def raise_error(ex):
    raise ex

@register(filters)
def clear_errors(tree, **kw):
    if isinstance(tree, Exception):

        tb = traceback.format_exc()
        if type(tree) is not MacroExpansionError:
            tree.args = (tree.args[0] + "\nCaused by Macro-Expansion Error:\n" + tb,)
        return hq[raise_error(tree)]
    else:
        return tree
