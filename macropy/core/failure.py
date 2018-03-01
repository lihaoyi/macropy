# -*- coding: utf-8 -*-
"""Transform macro expansion errors into runtime errors with nice
stack traces.
"""
import traceback

from .macros import filters
from .hquotes import macros, hq  # noqa: F401
from .util import register


class MacroExpansionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def raise_error(ex):
    raise ex


@register(filters)
def clear_errors(tree, **kw):
    if isinstance(tree, Exception):
        tb = "".join(traceback.format_tb(tree.__traceback__))
        msg = str(tree)
        if type(tree) is not AssertionError or tree.args == ():
            msg = ("".join(tree.args) + "\nCaused by Macro-Expansion Error:\n" +
                   tb)
        return hq[raise_error(MacroExpansionError(msg))]
    else:
        return tree
