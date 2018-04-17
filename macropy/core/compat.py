# -*- coding: utf-8 -*-

import ast
import sys

PY33 = sys.version_info >= (3, 3)
PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)
PY36 = sys.version_info >= (3, 6)

CPY = sys.implementation.name == 'cpython'
PYPY = sys.implementation.name == 'pypy'

HAS_FSTRING = CPY and PY36 or PYPY and PY35

if PY34:
    function_nodes = (ast.FunctionDef,)
else:
    function_nodes = (ast.AsyncFunctionDef, ast.FunctionDef)

scope_nodes = function_nodes + (ast.ClassDef,)


def Call(func, args, keywords):
    """A version of ``ast.Call`` that deals with compatibility.

    .. warning::

      Currently it supports only one element for each *args and **kwargs.
    """
    if PY35:
        return ast.Call(func, args, keywords)
    else:
        # see https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Call
        starargs = [el.value for el in args if isinstance(el, ast.Starred)]
        if len(starargs) == 0:
            starargs = None
        elif len(starargs) == 1:
            starargs = starargs[0]
        else:
            raise ValueError("No more than one starargs.")
        kwargs = [el.value for el in keywords if el.arg is None]
        if len(kwargs) == 0:
            kwargs = None
        elif len(kwargs) == 1:
            kwargs = kwargs[0]
        else:
            raise ValueError("No more than one kwargs.")
        args = [el for el in args if not isinstance(el, ast.Starred)]
        keywords = [el for el in keywords if el.value is not kwargs]
        return ast.Call(func, args, keywords, starargs, kwargs)
