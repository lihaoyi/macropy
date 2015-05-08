"""Transform macro expansion errors into runtime errors with nice stack traces.
T"""


import macropy.core.macros

from macropy.core.hquotes import macros, hq
import traceback
from six import PY3

from macropy.core.util import register


class MacroExpansionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def raise_error(ex):
    raise ex

@register(macropy.core.macros.filters)
def clear_errors(tree, **kw):
    if isinstance(tree, Exception):
        if macropy.core.macros.PY3: tb = "".join(traceback.format_tb(tree.__traceback__))
        else:   tb = traceback.format_exc()
        #msg = tree.message
        msg = str(tree)
        if type(tree) is not AssertionError or tree.args == ():
            msg = "".join(tree.args) + "\nCaused by Macro-Expansion Error:\n" + tb
        return hq[raise_error(MacroExpansionError(msg))]
    else:
        return tree
