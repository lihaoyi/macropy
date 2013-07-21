"""Transform macro expansion errors into runtime errors with nice stack traces.
T"""

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
        msg = tree.message
        if type(tree) is not AssertionError or tree.args == ():
            msg = "".join(tree.args) + "\nCaused by Macro-Expansion Error:\n" + tb
        return hq[raise_error(MacroExpansionError(msg))]
    else:
        return tree
