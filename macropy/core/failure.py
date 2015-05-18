"""Transform macro expansion errors into runtime errors with nice stack traces.
T"""

from __future__ import print_function

import ast
import sys
import traceback

from six import PY3

import macropy.core.macros
from macropy.core.hquotes import macros, hq
from macropy.core.util import register


class MacroExpansionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def raise_error(ex):
    raise ex

@register(macropy.core.macros.filters)
def clear_errors(tree, **kw):
    if isinstance(tree, Exception):
        # print(macropy.core.macros.filters, file=sys.stderr)
        if PY3: tb = "".join(traceback.format_tb(tree.__traceback__))
        else:   tb = traceback.format_exc()
        #msg = tree.message
        msg = str(tree)
        if type(tree) is not AssertionError or tree.args == ():
            msg = "".join(tree.args) + "\nCaused by Macro-Expansion Error:\n" + tb
        return hq[raise_error(MacroExpansionError(msg))]
    else:
        return tree
